#!/usr/bin/env python3
"""
Wallet Scanner GUI - Main Window Module

This module contains the main application window for the Wallet Scanner GUI.
It provides a comprehensive interface for cryptocurrency wallet forensic scanning.

Features:
- File and directory selection with native file dialogs
- Real-time scanner output monitoring
- Results visualization with filtering capabilities
- Device and image mounting support
- Multi-format export functionality
"""

import os
import re
import sys
import time
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QTextCursor

from ..core.config import APP_NAME, DEFAULT_HELP_HTML
from ..core.utils import quoted
try:
    from ..cli.cli_main import WalletScannerCLI
except ImportError:
    WalletScannerCLI = None


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for the Wallet Scanner GUI.
    
    This class provides a comprehensive interface for managing cryptocurrency
    wallet forensic scanning operations, including target selection, scanner
    configuration, and results visualization.
    
    Attributes:
        proc: Currently running scanner process
        last_out: Path to last scanner output directory
        hits_rows: List of scan result hits
        start_ts: Scan start timestamp
        timer: Timer for elapsed time updates
    """
    
    proc: Optional[QtCore.QProcess] = None
    cli_proc: Optional[QtCore.QProcess] = None
    last_out: Optional[Path] = None
    hits_rows: List[Tuple[str, int, str]] = []
    start_ts: float = 0.0
    timer: Optional[QtCore.QTimer] = None

    def __init__(self):
        """Initialize the main window with all UI components."""
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._populate_scanner_list()
        self._log_startup_info()

    def _setup_window(self):
        """Configure the main window properties."""
        self.setWindowTitle(APP_NAME)
        self.resize(1050, 650)
        
        # Set window icon if available
        icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))

    def _setup_ui(self):
        """Set up the user interface components."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # Top row: ROOT path and scanner selection
        self._setup_top_row(main_layout)
        
        # Middle section: Target list and management buttons
        self._setup_target_section(main_layout)
        
        # Options checkboxes and action buttons
        self._setup_options_section(main_layout)
        
        # Terminal option
        self._setup_terminal_option(main_layout)
        
        # Utility buttons
        self._setup_utility_buttons(main_layout)
        
        # Main tabs for results and help
        self._setup_tabs(main_layout)

    def _setup_top_row(self, parent_layout):
        """Set up the top row with ROOT path and scanner selection."""
        top_layout = QtWidgets.QHBoxLayout()
        
        # ROOT path configuration
        top_layout.addWidget(QtWidgets.QLabel("ROOT:"))
        self.rootEdit = QtWidgets.QLineEdit(str(Path("/run/media/emil/DATEN")))
        self.btnRoot = QtWidgets.QPushButton("ROOT wählen…")
        self.btnRoot.clicked.connect(self.choose_root)
        top_layout.addWidget(self.rootEdit, 1)
        top_layout.addWidget(self.btnRoot)
        
        # Scanner selection
        top_layout.addWidget(QtWidgets.QLabel("Scanner:"))
        self.scannerCombo = QtWidgets.QComboBox()
        self.scannerCombo.currentTextChanged.connect(self.on_scanner_changed)
        top_layout.addWidget(self.scannerCombo, 2)
        
        self.btnScanner = QtWidgets.QPushButton("Eigener Scanner…")
        self.btnScanner.clicked.connect(self.choose_scanner)
        top_layout.addWidget(self.btnScanner)
        
        parent_layout.addLayout(top_layout)

    def _setup_target_section(self, parent_layout):
        """Set up the target list and management buttons."""
        mid_layout = QtWidgets.QHBoxLayout()
        
        # Target list widget
        self.targets = QtWidgets.QListWidget()
        self.targets.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        mid_layout.addWidget(self.targets, 1)
        
        # Target management buttons
        button_layout = QtWidgets.QVBoxLayout()
        buttons = [
            ("Ordner hinzufügen", self.add_dir),
            ("Datei/Abbild hinzufügen", self.add_file),
            ("Device (/dev/…) hinzufügen", self.add_dev),
            ("Auswahl entfernen", self.rm_selected),
            ("Liste leeren", self.targets.clear),
        ]
        
        for text, callback in buttons:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        
        button_layout.addStretch(1)
        mid_layout.addLayout(button_layout)
        parent_layout.addLayout(mid_layout, 1)

    def _setup_options_section(self, parent_layout):
        """Set up the options checkboxes and action buttons."""
        opts_layout = QtWidgets.QHBoxLayout()
        
        # Option checkboxes
        self.chkAgg = QtWidgets.QCheckBox("Aggressiv")
        self.chkStage = QtWidgets.QCheckBox("Staging anlegen (Symlinks)")
        self.chkRoot = QtWidgets.QCheckBox("Mit Root (pkexec) für Auto-Mount")
        self.chkAutoMount = QtWidgets.QCheckBox("Auto-Mount für Images/Devices")
        self.chkAutoMount.setChecked(True)
        
        for widget in (self.chkAgg, self.chkStage, self.chkRoot, self.chkAutoMount):
            opts_layout.addWidget(widget)
        
        opts_layout.addStretch(1)
        
        # Action buttons
        self.btnScan = QtWidgets.QPushButton("Scan starten")
        self.btnScan.clicked.connect(self.start_scan)
        self.btnStop = QtWidgets.QPushButton("Stop")
        self.btnStop.setEnabled(False)
        self.btnStop.clicked.connect(self.stop_scan)
        
        opts_layout.addWidget(self.btnScan)
        opts_layout.addWidget(self.btnStop)
        parent_layout.addLayout(opts_layout)

    def _setup_terminal_option(self, parent_layout):
        """Set up the terminal display option."""
        opts2_layout = QtWidgets.QHBoxLayout()
        self.chkShowTerminal = QtWidgets.QCheckBox("🖥️ Terminal-Fenster beim Scan zeigen")
        self.chkShowTerminal.setToolTip(
            "Öffnet externes Terminal mit Live-Scanner-Output\n"
            "Nützlich für Debugging und Transparenz"
        )
        opts2_layout.addWidget(self.chkShowTerminal)
        opts2_layout.addStretch(1)
        parent_layout.addLayout(opts2_layout)

    def _setup_utility_buttons(self, parent_layout):
        """Set up utility buttons for quick access to directories."""
        util_layout = QtWidgets.QHBoxLayout()
        
        utilities = [
            ("ROOT in Dolphin", lambda: self.open_path(self.rootEdit.text())),
            ("Staging öffnen", lambda: self.open_path(
                str(Path(self.rootEdit.text()) / "Software/_staging_wallets")
            )),
            ("Logs öffnen", self.open_logs),
        ]
        
        for text, callback in utilities:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(callback)
            util_layout.addWidget(btn)
        
        util_layout.addStretch(1)
        parent_layout.addLayout(util_layout)

    def _setup_tabs(self, parent_layout):
        """Set up the main tab widget for results and documentation."""
        self.tabs = QtWidgets.QTabWidget()
        parent_layout.addWidget(self.tabs, 5)
        
        # Live log tab
        self._setup_live_log_tab()
        
        # CLI Tools tab
        self._setup_cli_tab()
        
        # Hits results tab
        self._setup_hits_tab()
        
        # Mnemonics tab
        self._setup_mnemonics_tab()
        
        # Help/instructions tab
        self._setup_help_tab()

    def _setup_live_log_tab(self):
        """Set up the live log tab for real-time scanner output."""
        live_widget = QtWidgets.QWidget()
        live_layout = QtWidgets.QVBoxLayout(live_widget)
        live_layout.setContentsMargins(6, 6, 6, 6)
        
        self.logView = QtWidgets.QPlainTextEdit()
        self.logView.setReadOnly(True)
        self.logView.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        live_layout.addWidget(self.logView, 1)
        
        self.statusLbl = QtWidgets.QLabel("Bereit")
        live_layout.addWidget(self.statusLbl, 0)
        
        self.tabs.addTab(live_widget, "Live-Log")

    def _setup_cli_tab(self):
        """Set up the CLI tools tab for direct command execution."""
        cli_widget = QtWidgets.QWidget()
        cli_layout = QtWidgets.QVBoxLayout(cli_widget)
        cli_layout.setContentsMargins(6, 6, 6, 6)
        
        # CLI commands section
        commands_layout = QtWidgets.QGridLayout()
        
        # System check
        check_btn = QtWidgets.QPushButton("🔍 System Check")
        check_btn.setToolTip("Überprüfe System-Anforderungen und verfügbare Scanner")
        check_btn.clicked.connect(self.run_cli_check)
        commands_layout.addWidget(check_btn, 0, 0)
        
        # Setup config
        setup_btn = QtWidgets.QPushButton("⚙️ Setup Config")
        setup_btn.setToolTip("Erstelle Konfigurationsverzeichnisse")
        setup_btn.clicked.connect(self.run_cli_setup)
        commands_layout.addWidget(setup_btn, 0, 1)
        
        # List scanners
        scanners_btn = QtWidgets.QPushButton("📝 List Scanners")
        scanners_btn.setToolTip("Zeige verfügbare Scanner-Skripte")
        scanners_btn.clicked.connect(self.run_cli_list_scanners)
        commands_layout.addWidget(scanners_btn, 0, 2)
        
        # Analyze path
        analyze_layout = QtWidgets.QHBoxLayout()
        self.analyze_path = QtWidgets.QLineEdit()
        self.analyze_path.setPlaceholderText("Pfad zur Analyse...")
        analyze_btn = QtWidgets.QPushButton("🔬 Analyze")
        analyze_btn.setToolTip("Analysiere Pfad auf Wallet-Inhalte")
        analyze_btn.clicked.connect(self.run_cli_analyze)
        
        analyze_layout.addWidget(QtWidgets.QLabel("Analyze:"))
        analyze_layout.addWidget(self.analyze_path, 1)
        analyze_layout.addWidget(analyze_btn)
        commands_layout.addLayout(analyze_layout, 1, 0, 1, 3)
        
        cli_layout.addLayout(commands_layout)
        
        # CLI output area
        cli_layout.addWidget(QtWidgets.QLabel("CLI Output:"))
        self.cli_output = QtWidgets.QPlainTextEdit()
        self.cli_output.setReadOnly(True)
        self.cli_output.setFont(QtGui.QFont("Consolas", 9))
        cli_layout.addWidget(self.cli_output, 1)
        
        self.tabs.addTab(cli_widget, "CLI Tools")

    def _setup_hits_tab(self):
        """Set up the hits tab for displaying scan results."""
        hits_widget = QtWidgets.QWidget()
        hits_layout = QtWidgets.QVBoxLayout(hits_widget)
        hits_layout.setContentsMargins(6, 6, 6, 6)
        
        # Filter and action controls
        filter_layout = QtWidgets.QHBoxLayout()
        
        self.hitFilter = QtWidgets.QLineEdit()
        self.hitFilter.setPlaceholderText(
            "Filter (Regex, z. B. bc1|0x|xpub|wallet\\.dat)"
        )
        self.hitFilter.textChanged.connect(self.refresh_hits_table)
        
        self.btnOpenSel = QtWidgets.QPushButton("Öffnen")
        self.btnOpenSel.clicked.connect(self.open_selected_hit)
        
        self.btnExport = QtWidgets.QPushButton("Export .tsv")
        self.btnExport.clicked.connect(self.export_hits)
        
        self.btnCopy = QtWidgets.QPushButton("Kopieren")
        self.btnCopy.clicked.connect(self.copy_hits)
        
        for widget in (self.hitFilter, self.btnOpenSel, self.btnExport, self.btnCopy):
            filter_layout.addWidget(widget)
        
        filter_layout.addStretch(1)
        hits_layout.addLayout(filter_layout)
        
        # Results table
        self.hitTable = QtWidgets.QTableWidget(0, 3)
        self.hitTable.setHorizontalHeaderLabels(["Datei", "Zeile", "Treffer-Snippet"])
        self.hitTable.horizontalHeader().setStretchLastSection(True)
        self.hitTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.hitTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        hits_layout.addWidget(self.hitTable, 1)
        
        self.tabs.addTab(hits_widget, "Hits")

    def _setup_mnemonics_tab(self):
        """Set up the mnemonics tab for seed phrase candidates."""
        self.mnemoView = QtWidgets.QPlainTextEdit()
        self.mnemoView.setReadOnly(True)
        self.tabs.addTab(self.mnemoView, "Mnemonics")

    def _setup_help_tab(self):
        """Set up the comprehensive help/instructions tab."""
        self.helpView = QtWidgets.QPlainTextEdit()
        self.helpView.setReadOnly(True)
        self.helpView.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.helpView.setPlainText(self._get_comprehensive_help_text())
        self.tabs.addTab(self.helpView, "Anleitung")

    def _get_comprehensive_help_text(self) -> str:
        """Generate comprehensive help text for the application."""
        return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WALLET GUI - SCANNER BEDIENUNGSANLEITUNG                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
 📂 HAUPTKONFIGURATION (Obere Zeile)
═══════════════════════════════════════════════════════════════════════════════

🔹 ROOT: /pfad/zum/arbeitsverzeichnis
   Zweck: Ausgangspfad für Scanner-Ergebnisse
   Was wird hier gespeichert:
     • _logs/ → Alle Scan-Ergebnisse (hits.txt, mnemonics, etc.)
     • Software/_staging_wallets/ → Symlinks zu Treffern (optional)
   
   Wann ändern:
     • Wenn Output woanders gespeichert werden soll
     • Wenn mehr Speicherplatz benötigt wird
   
   💡 Tipp: Sollte auf schneller Platte liegen (nicht USB 2.0!)

🔹 ROOT wählen... [Button]
   Öffnet Dialog zur Auswahl des ROOT-Verzeichnisses
   • Nutzt kdialog (KDE-native) oder Qt-Dialog als Fallback
   • Dialog-Größe: 1200x800 Pixel für bessere Übersicht
   • Shortcuts: /, /home, /run/media, /mnt, /media

🔹 Scanner: [Dropdown]
   Zweck: Auswahl des Scanner-Skripts
   
   Verfügbare Scanner:
     • wallet_harvest_any.sh → Legacy-Scanner (Standard)
     • hrm_swarm_scanner_wrapper.sh → Modern mit Auto-Mount ⭐ EMPFOHLEN!
     • wallet_scan_archives.sh → Spezialisiert auf Archive
     • wallet_scan_images.sh → Spezialisiert auf Images
     • Eigene Scanner (mit "Eigener Scanner..." hinzufügen)
   
   ⚡ Empfehlung: hrm_swarm_scanner_wrapper.sh für Auto-Mount-Features!

═══════════════════════════════════════════════════════════════════════════════
 🎯 TARGET-LISTE & MANAGEMENT (Mitte)
═══════════════════════════════════════════════════════════════════════════════

🔹 Große Liste (leer oder mit Einträgen)
   Zeigt alle Scan-Targets:
     • Ordner: /path/to/directory
     • Dateien: /path/to/file.img
     • Devices: /dev/sda1 oder /dev/disk/by-label/USB_STICK
     • Archive: /path/to/backup.zip
   
   Multi-Selektion:
     • Strg+Klick → Einzelne Targets wählen
     • Shift+Klick → Bereich wählen

🔹 Ordner hinzufügen [Button]
   Fügt Verzeichnis(se) zur Scan-Liste hinzu
   
   Was passiert:
     • Öffnet kdialog mit Multi-Selektion
     • Startet in ROOT oder /run/media
     • Mehrere Ordner mit Strg+Klick möglich
     • Duplikat-Schutz: Keine doppelten Einträge

═══════════════════════════════════════════════════════════════════════════════
 ⚙️ OPTIONEN (Checkboxen)
═══════════════════════════════════════════════════════════════════════════════

☐ Aggressiv
   Intensiverer Scan mit mehr Features
   
   Was ändert sich:
     ✓ Threads: 10 (statt 6) → Schneller bei vielen CPUs
     ✓ Max Dateigröße: 1024 MB = 1 GB (statt 512 MB)
     ✓ YARA-Scan aktiviert → Wallet-Pattern-Erkennung
     ✓ Mehr Dateitypen durchsucht

☑ Auto-Mount für Images/Devices ⚠️ WICHTIG!
   Automatisches Mounten von Images/Devices
   (Standard: AKTIVIERT)
   
   Was passiert:
     → Images (.img, .iso, .dd): Read-only mounten
     → Archive (.zip, .7z, .tar): Extrahieren
     → Devices (/dev/sdX): Read-only mounten
     → Nach Scan: Automatisches Unmount/Cleanup

═══════════════════════════════════════════════════════════════════════════════
 📊 TABS (Ergebnisse & Info)
═══════════════════════════════════════════════════════════════════════════════

🔹 Live-Log Tab
   Scanner-Output in Echtzeit
   
   Features:
     ✓ Auto-Scroll (scrollt automatisch mit)
     ✓ Timer unten (Elapsed-Zeit)
     ✓ Status-Label ("Bereit", "Läuft...", "Fertig")

🔹 Hits Tab
   Gefundene Treffer anzeigen
   
   Features:
     ✓ Regex-Filter: bc1|0x|xpub|wallet\\.dat
     ✓ "Öffnen" Button → Datei im Editor öffnen
     ✓ "Export .tsv" → Alle Treffer exportieren
     ✓ "Kopieren" → Treffer in Zwischenablage

🔹 Mnemonics Tab
   Seed-Phrase-Kandidaten anzeigen

═══════════════════════════════════════════════════════════════════════════════
 💡 ZUSAMMENFASSUNG
═══════════════════════════════════════════════════════════════════════════════

1. ROOT setzen (wo Ergebnisse gespeichert werden)
2. Scanner wählen (hrm_swarm_scanner_wrapper.sh empfohlen!)
3. Targets hinzufügen (Ordner/Dateien/Devices)
4. Optionen wählen (Root + Auto-Mount für Images/Devices)
5. "Scan starten" klicken
6. "Live-Log" beobachten
7. "Hits" Tab prüfen!

═══════════════════════════════════════════════════════════════════════════════
        """

    def _populate_scanner_list(self):
        """Populate the scanner dropdown with available scanners from scripts directory."""
        scripts_dir = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
        
        scanners = []
        if scripts_dir.exists():
            # Collect all .sh and .py files
            for pattern in ("*.sh", "*.py"):
                scanners.extend(scripts_dir.glob(pattern))
        
        # Sort by name
        scanners.sort(key=lambda p: p.name)
        
        # Default scanner
        default_scanner = scripts_dir / "wallet_harvest_any.sh"
        
        self.scannerCombo.clear()
        for scanner in scanners:
            # Show only filename in dropdown
            display_name = scanner.name
            # Store full path as userData
            self.scannerCombo.addItem(display_name, str(scanner))
        
        # Set default scanner
        if default_scanner.exists():
            idx = self.scannerCombo.findData(str(default_scanner))
            if idx >= 0:
                self.scannerCombo.setCurrentIndex(idx)

    def _log_startup_info(self):
        """Log startup information and recommended packages."""
        self.append_log(
            "Hinweis: Empfohlene Pakete: python3-pyqt6 kdialog p7zip "
            "p7zip-plugins sleuthkit ntfs-3g\n"
        )

    # Event handlers and utility methods
    
    def on_scanner_changed(self, text: str):
        """Called when a scanner is selected from the dropdown."""
        pass  # Scanner path is stored in userData

    def get_current_scanner(self) -> str:
        """Get the path of the currently selected scanner."""
        return self.scannerCombo.currentData() or ""

    def append_log(self, text: str):
        """Append text to the log view with auto-scroll."""
        self.logView.appendPlainText(text.rstrip("\n"))
        self.logView.moveCursor(QTextCursor.MoveOperation.End)

    # File and directory selection methods
    
    def choose_root(self):
        """Choose ROOT directory using native file dialog."""
        if shutil.which("kdialog"):
            initial = self.rootEdit.text() or "/run/media"
            result = subprocess.run(
                ["kdialog", "--title", "ROOT-Verzeichnis auswählen", 
                 "--getexistingdirectory", initial],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                selected = result.stdout.strip()
                self.rootEdit.setText(selected)
                self.append_log(f"✓ ROOT gesetzt: {selected}\n")
                return
        
        # Fallback: Qt dialog
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("ROOT-Verzeichnis auswählen")
        dialog.setDirectory(self.rootEdit.text() or "/")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        dialog.resize(1200, 800)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            directory = dialog.selectedFiles()[0]
            if directory:
                self.rootEdit.setText(directory)

    def choose_scanner(self):
        """Choose custom scanner script."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Scanner-Skript wählen")
        
        # Set directory to scripts/ (not standalone/)
        scripts_dir = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
        if scripts_dir.exists():
            dialog.setDirectory(str(scripts_dir))
        else:
            dialog.setDirectory(str(Path.home()))
        
        dialog.setNameFilter("Shell-Skripte (*.sh);;Python-Skripte (*.py);;Alle Dateien (*)")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        dialog.resize(1200, 800)
        
        # Add shortcuts
        shortcuts = [
            QtCore.QUrl.fromLocalFile(str(scripts_dir)),
            QtCore.QUrl.fromLocalFile(str(Path.home() / ".local" / "share" / "wallet-gui")),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            file_path = dialog.selectedFiles()[0]
            if file_path:
                # Warn if standalone/ was chosen
                if "standalone" in file_path:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Warnung: Standalone-Scanner",
                        f"Der gewählte Scanner ist ein Standalone-Scanner:\n{file_path}\n\n"
                        "Standalone-Scanner sind NICHT GUI-kompatibel und müssen direkt\n"
                        "über die Kommandozeile ausgeführt werden.\n\n"
                        "Bitte wählen Sie einen Scanner aus dem scripts/ Ordner."
                    )
                    return
                
                # Add custom scanner to combo box
                display_name = f"⭐ {Path(file_path).name}"
                self.scannerCombo.addItem(display_name, file_path)
                self.scannerCombo.setCurrentIndex(self.scannerCombo.count() - 1)
                self.append_log(f"✓ Custom-Scanner gewählt: {Path(file_path).name}\n")

    def add_dir(self):
        """Add directories to scan list using native file dialog."""
        if shutil.which("kdialog"):
            # Use kdialog - supports multi-selection
            initial = self.rootEdit.text() or "/run/media"
            result = subprocess.run(
                ["kdialog", "--title", "Ordner hinzufügen (Mehrfachauswahl mit Strg)",
                 "--multiple", "--separate-output", "--getexistingdirectory", initial],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for path in result.stdout.strip().split('\n'):
                    if path and not self.targets.findItems(path, QtCore.Qt.MatchFlag.MatchExactly):
                        self.targets.addItem(path)
                        self.append_log(f"✓ Ordner hinzugefügt: {path}\n")
                return
        
        # Fallback: Qt dialog with enhanced configuration
        self._add_dir_qt_dialog()

    def _add_dir_qt_dialog(self):
        """Fallback Qt dialog for directory selection."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Ordner hinzufügen (Mehrfachauswahl möglich)")
        dialog.setDirectory(self.rootEdit.text() or "/")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QtWidgets.QFileDialog.Option.ShowDirsOnly, False)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        dialog.resize(1200, 800)
        
        # Add shortcuts for quick access
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/"),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
            QtCore.QUrl.fromLocalFile("/run/media"),
            QtCore.QUrl.fromLocalFile("/mnt"),
            QtCore.QUrl.fromLocalFile("/media"),
            QtCore.QUrl.fromLocalFile("/dev"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for directory in dialog.selectedFiles():
                if directory and not self.targets.findItems(directory, QtCore.Qt.MatchFlag.MatchExactly):
                    self.targets.addItem(directory)
                    self.append_log(f"✓ Ziel hinzugefügt: {directory}\n")

    def add_file(self):
        """Add files/images to scan list using native file dialog."""
        if shutil.which("kdialog"):
            # Use kdialog - supports multi-selection and filters
            initial = self.rootEdit.text() or "/run/media"
            
            # Filters for kdialog
            filters = (
                "*.img *.IMG *.iso *.ISO *.dd *.DD *.raw *.RAW *.vhd *.vhdx *.vmdk *.qcow2|Disk-Images\n"
                "*.zip *.ZIP *.rar *.RAR *.7z *.7Z *.tar *.TAR *.tar.gz *.tgz *.TGZ|Archive\n"
                "*|Alle Dateien"
            )
            
            result = subprocess.run(
                ["kdialog", "--title", "Datei/Abbild hinzufügen (Mehrfachauswahl mit Strg)",
                 "--multiple", "--separate-output", "--getopenfilename", initial, filters],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for path in result.stdout.strip().split('\n'):
                    if path and not self.targets.findItems(path, QtCore.Qt.MatchFlag.MatchExactly):
                        size = Path(path).stat().st_size if Path(path).exists() else 0
                        size_mb = size / (1024 * 1024)
                        self.targets.addItem(path)
                        self.append_log(f"✓ Datei hinzugefügt: {path} ({size_mb:.1f} MB)\n")
                return
        
        # Fallback: Qt dialog
        self._add_file_qt_dialog()

    def _add_file_qt_dialog(self):
        """Fallback Qt dialog for file selection."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Datei/Abbild hinzufügen (Mehrfachauswahl möglich)")
        dialog.setDirectory(self.rootEdit.text() or "/")
        
        # Filter with "All files" as default
        dialog.setNameFilter(
            "Alle Dateien (*);;Disk-Images (*.img *.IMG *.iso *.ISO *.dd *.DD "
            "*.raw *.RAW *.vhd *.vhdx *.vmdk *.qcow2);;Archive (*.zip *.ZIP "
            "*.rar *.RAR *.7z *.7Z *.tar *.TAR *.tar.gz *.tgz *.TGZ)"
        )
        dialog.selectNameFilter("Alle Dateien (*)")
        
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        dialog.resize(1200, 800)
        
        # Add shortcuts
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/"),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
            QtCore.QUrl.fromLocalFile("/run/media"),
            QtCore.QUrl.fromLocalFile("/mnt"),
            QtCore.QUrl.fromLocalFile("/media"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for file_path in dialog.selectedFiles():
                if file_path and not self.targets.findItems(file_path, QtCore.Qt.MatchFlag.MatchExactly):
                    size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                    size_mb = size / (1024 * 1024)
                    self.targets.addItem(file_path)
                    self.append_log(f"✓ Ziel hinzugefügt: {file_path} ({size_mb:.1f} MB)\n")

    def add_dev(self):
        """Add block devices to scan list using native file dialog."""
        if shutil.which("kdialog"):
            # Use kdialog for device selection
            initial = "/dev/disk/by-label"
            if not Path(initial).exists():
                initial = "/dev"
            
            result = subprocess.run(
                ["kdialog", "--title", "Device wählen (Mehrfachauswahl mit Strg)",
                 "--multiple", "--separate-output", "--getopenfilename", initial],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for path in result.stdout.strip().split('\n'):
                    if path and not self.targets.findItems(path, QtCore.Qt.MatchFlag.MatchExactly):
                        self.targets.addItem(path)
                        self.append_log(f"✓ Device hinzugefügt: {path}\n")
                
                # Check if root options are enabled
                self._check_device_requirements()
                return
        
        # Fallback: Qt dialog
        self._add_dev_qt_dialog()

    def _add_dev_qt_dialog(self):
        """Fallback Qt dialog for device selection."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Device wählen (/dev/...)")
        dialog.setDirectory("/dev")
        dialog.setNameFilter("Block-Devices (sd* nvme* mmcblk* vd* hd* loop*);;Alle Dateien (*)")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        dialog.resize(1200, 800)
        
        # Add device-specific shortcuts
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/dev"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-id"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-uuid"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-label"),
            QtCore.QUrl.fromLocalFile("/sys/block"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for file_path in dialog.selectedFiles():
                if file_path and not self.targets.findItems(file_path, QtCore.Qt.MatchFlag.MatchExactly):
                    self.targets.addItem(file_path)
                    self.append_log(f"✓ Device hinzugefügt: {file_path}\n")
            
            self._check_device_requirements()

    def _check_device_requirements(self):
        """Check if required options are enabled for device scanning."""
        if not self.chkRoot.isChecked() or not self.chkAutoMount.isChecked():
            QtWidgets.QMessageBox.warning(
                self,
                "Device-Scanning",
                "⚠️ Sie haben Devices hinzugefügt.\n\n"
                "Für Device-Scanning benötigen Sie:\n"
                "  ✓ 'Mit Root (pkexec)' aktiviert\n"
                "  ✓ 'Auto-Mount' aktiviert\n\n"
                "Bitte aktivieren Sie diese Optionen vor dem Scan!"
            )

    def rm_selected(self):
        """Remove selected targets from the list."""
        for item in self.targets.selectedItems():
            self.targets.takeItem(self.targets.row(item))

    def open_path(self, path_str: str):
        """Open path in file manager."""
        if not path_str:
            return
        
        path = Path(path_str)
        if not path.exists():
            QtWidgets.QMessageBox.warning(
                self, "Öffnen", f"Pfad existiert nicht:\n{path_str}"
            )
            return
        
        if path.is_file() and shutil.which("dolphin"):
            subprocess.Popen(["dolphin", "--select", str(path)])
        else:
            target = path if path.is_dir() else path.parent
            subprocess.Popen(["xdg-open", str(target)])

    def open_logs(self):
        """Open the logs directory."""
        if self.last_out and self.last_out.exists():
            subprocess.Popen(["xdg-open", str(self.last_out)])
        else:
            logs_dir = Path(self.rootEdit.text()) / "_logs"
            subprocess.Popen(["xdg-open", str(logs_dir)])

    # Scanner execution methods
    
    def start_scan(self):
        """Start the scanner process with current configuration."""
        if self.proc:
            QtWidgets.QMessageBox.information(
                self, "Läuft", "Ein Scan läuft bereits."
            )
            return
        
        # Validate configuration
        root = self.rootEdit.text().strip()
        if not root:
            QtWidgets.QMessageBox.warning(self, "Fehler", "ROOT ist leer.")
            return
        
        script = self.get_current_scanner()
        if not script or not Path(script).exists():
            QtWidgets.QMessageBox.warning(
                self, "Fehler", f"Scanner-Skript nicht gefunden:\n{script}"
            )
            return

        # Get targets
        targets = [self.targets.item(i).text() for i in range(self.targets.count())]
        if not targets:
            # Use default targets if none specified
            defaults = []
            for sub in ("_mount/hitachi_sdc3_ntfs", "_recovery", "Software/Collected"):
                path = Path(root) / sub
                if path.exists():
                    defaults.append(str(path))
            targets = defaults

        # Build command arguments
        args = [script, root]
        if self.chkAgg.isChecked():
            args.append("--aggressive")
        if self.chkStage.isChecked():
            args.append("--staging")
        if self.chkAutoMount.isChecked():
            args.append("--auto-mount")
        args.extend(targets)

        # Build command with optional root privileges
        cmd = ["bash", "-lc", " ".join(quoted(arg) for arg in args)]
        if self.chkRoot.isChecked():
            cmd = ["pkexec"] + cmd

        # Log command execution
        self.append_log(f"\n== Starte ==\n{' '.join(args)}\n")
        
        # Reset state
        self.last_out = None
        self.btnScan.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.start_ts = time.time()
        self.statusLbl.setText("Läuft …")
        
        # Start timer for elapsed time updates
        if self.timer:
            self.timer.stop()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_elapsed)
        self.timer.start(500)

        # Start scanner process
        if self.chkShowTerminal.isChecked():
            self.open_scanner_terminal(cmd)
        else:
            self._start_gui_scanner(cmd)

    def _start_gui_scanner(self, cmd: List[str]):
        """Start scanner in GUI mode with output capture."""
        self.proc = QtCore.QProcess(self)
        self.proc.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self.on_proc_out)
        self.proc.finished.connect(self.on_proc_finished)
        self.proc.start(cmd[0], cmd[1:])

    def open_scanner_terminal(self, cmd: List[str]):
        """Open external terminal window for scanner execution."""
        import tempfile
        
        # Create temporary wrapper script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            wrapper = f.name
            f.write(f"""#!/bin/bash
# Wallet Scanner Terminal
echo "═══════════════════════════════════════════════════════════"
echo " 🔍 Wallet Scanner - Live Output"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Scanner: {self.get_current_scanner()}"
echo "ROOT: {self.rootEdit.text()}"
echo "Targets: {self.targets.count()}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Execute scanner
{' '.join(quoted(c) for c in cmd)}

EXIT_CODE=$?
echo ""
echo "═══════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo " ✅ Scanner erfolgreich beendet"
else
    echo " ❌ Scanner mit Fehler beendet (Exit Code: $EXIT_CODE)"
fi
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Drücke Enter um Fenster zu schließen..."
read
""")
        
        os.chmod(wrapper, 0o755)
        
        # Detect terminal emulator
        terminals = [
            ("konsole", ["konsole", "--hold", "-e", "bash", wrapper]),
            ("gnome-terminal", ["gnome-terminal", "--wait", "--", "bash", wrapper]),
            ("xfce4-terminal", ["xfce4-terminal", "--hold", "-e", f"bash {wrapper}"]),
            ("xterm", ["xterm", "-hold", "-e", "bash", wrapper]),
            ("x-terminal-emulator", ["x-terminal-emulator", "-e", f"bash {wrapper}; read"]),
        ]
        
        terminal_cmd = None
        for name, term_cmd in terminals:
            if shutil.which(name):
                terminal_cmd = term_cmd
                self.append_log(f"🖥️ Öffne Terminal: {name}\n")
                break
        
        if not terminal_cmd:
            self._handle_no_terminal_found(cmd)
            return
        
        # Start terminal process
        self.proc = QtCore.QProcess(self)
        self.proc.finished.connect(self.on_proc_finished_terminal)
        self.proc.start(terminal_cmd[0], terminal_cmd[1:])
        
        # Schedule wrapper cleanup (after 5 minutes)
        QtCore.QTimer.singleShot(300000, lambda: self.cleanup_wrapper(wrapper))

    def _handle_no_terminal_found(self, cmd: List[str]):
        """Handle case when no terminal emulator is found."""
        QtWidgets.QMessageBox.warning(
            self,
            "Kein Terminal gefunden",
            "Kein Terminal-Emulator gefunden!\n\n"
            "Bitte installiere einen:\n"
            "• konsole (KDE)\n"
            "• gnome-terminal (GNOME)\n"
            "• xfce4-terminal (XFCE)\n"
            "• xterm (Fallback)\n\n"
            "Scan wird im GUI-Modus fortgesetzt."
        )
        self.chkShowTerminal.setChecked(False)
        self._start_gui_scanner(cmd)

    def cleanup_wrapper(self, wrapper: str):
        """Clean up temporary wrapper script."""
        try:
            if os.path.exists(wrapper):
                os.remove(wrapper)
        except Exception:
            pass

    def stop_scan(self):
        """Stop the currently running scanner process."""
        if not self.proc:
            return
        
        try:
            self.proc.terminate()
            if not self.proc.waitForFinished(2000):
                self.proc.kill()
        finally:
            self.proc = None
            self.btnScan.setEnabled(True)
            self.btnStop.setEnabled(False)
            self.statusLbl.setText("Abgebrochen")
            if self.timer:
                self.timer.stop()

    def update_elapsed(self):
        """Update elapsed time display."""
        if not self.start_ts:
            return
        
        elapsed = int(time.time() - self.start_ts)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.statusLbl.setText(f"Läuft … {hours:02d}:{minutes:02d}:{seconds:02d}")

    def on_proc_out(self):
        """Handle process output from scanner."""
        if not self.proc:
            return
        
        data = bytes(self.proc.readAllStandardOutput()).decode(errors="ignore")
        if not data:
            return
        
        self.append_log(data)
        
        # Extract output directory from scanner output
        match = re.search(r"OUT=(\S+)", data)
        if match:
            self.last_out = Path(match.group(1))

    def on_proc_finished(self, exit_code, exit_status):
        """Handle scanner process completion."""
        self.append_log("\n== Fertig ==\n")
        self.btnScan.setEnabled(True)
        self.btnStop.setEnabled(False)
        if self.timer:
            self.timer.stop()
        self.statusLbl.setText("Fertig")
        self.proc = None
        self.load_results()

    def on_proc_finished_terminal(self, exit_code, exit_status):
        """Handle terminal process completion."""
        self.append_log("\n🖥️ Terminal-Fenster geschlossen\n")
        self.append_log("\n== Fertig ==\n")
        self.btnScan.setEnabled(True)
        self.btnStop.setEnabled(False)
        if self.timer:
            self.timer.stop()
        self.statusLbl.setText("Fertig")
        self.proc = None
        
        # Wait briefly then load results
        QtCore.QTimer.singleShot(1000, self.load_results)

    # Results handling methods
    
    def load_results(self):
        """Load scan results from output directory."""
        output_dir = self.last_out
        if not output_dir or not output_dir.exists():
            logs_dir = Path(self.rootEdit.text()) / "_logs"
            if logs_dir.exists():
                scans = sorted(
                    logs_dir.glob("walletscan_*"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                if scans:
                    output_dir = scans[0]
        
        if not output_dir or not output_dir.exists():
            return

        # Load hits
        hits_file = output_dir / "hits.txt"
        self.hits_rows = []
        if hits_file.exists():
            for line in hits_file.read_text(errors="ignore").splitlines():
                match = re.match(r"^(.*?):(\d+):(.*)$", line)
                if match:
                    self.hits_rows.append((
                        match.group(1),
                        int(match.group(2)),
                        match.group(3).strip()
                    ))
        
        self.refresh_hits_table()

        # Load mnemonics
        mnemonics_file = output_dir / "mnemonic_raw.txt"
        content = "(keine Kandidaten)"
        if mnemonics_file.exists():
            content = mnemonics_file.read_text(errors="ignore")
        self.mnemoView.setPlainText(content)

    def refresh_hits_table(self):
        """Refresh the hits table with current filter applied."""
        filter_text = self.hitFilter.text().strip()
        regex = None
        
        if filter_text:
            try:
                regex = re.compile(filter_text, re.IGNORECASE)
            except re.error:
                regex = None
        
        # Apply filter
        filtered_rows = []
        for row in self.hits_rows:
            if regex:
                combined_text = " ".join([row[0], str(row[1]), row[2]])
                if regex.search(combined_text):
                    filtered_rows.append(row)
            else:
                filtered_rows.append(row)
        
        # Update table
        table = self.hitTable
        table.setRowCount(0)
        table.setSortingEnabled(False)
        
        for file_path, line_num, snippet in filtered_rows:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(file_path))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(line_num)))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(snippet))
        
        table.setSortingEnabled(True)
        table.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def selected_hit(self) -> Optional[Tuple[str, int, str]]:
        """Get the currently selected hit from the table."""
        row = self.hitTable.currentRow()
        if row < 0:
            return None
        
        return (
            self.hitTable.item(row, 0).text(),
            int(self.hitTable.item(row, 1).text()),
            self.hitTable.item(row, 2).text()
        )

    def open_selected_hit(self):
        """Open the selected hit file in file manager."""
        selected = self.selected_hit()
        if not selected:
            return
        
        file_path = Path(selected[0])
        if shutil.which("dolphin"):
            subprocess.Popen(["dolphin", "--select", str(file_path)])
        else:
            subprocess.Popen(["xdg-open", str(file_path.parent)])

    def export_hits(self):
        """Export hits as TSV file (respecting current filter)."""
        import csv
        
        filter_text = self.hitFilter.text().strip()
        regex = None
        
        if filter_text:
            try:
                regex = re.compile(filter_text, re.IGNORECASE)
            except re.error:
                regex = None
        
        # Apply filter
        filtered_rows = []
        for row in self.hits_rows:
            if regex:
                combined_text = " ".join([row[0], str(row[1]), row[2]])
                if regex.search(combined_text):
                    filtered_rows.append(row)
            else:
                filtered_rows.append(row)
        
        if not filtered_rows:
            QtWidgets.QMessageBox.information(
                self, "Export", "Keine Treffer zum Exportieren."
            )
            return
        
        # Get save path
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export als TSV", "hits.tsv", "TSV (*.tsv);;Alle Dateien (*)"
        )
        
        if not path:
            return
        
        # Write TSV file
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["file", "line", "snippet"])
            for row in filtered_rows:
                writer.writerow(row)
        
        self.append_log(f"Exportiert: {path}\n")

    def copy_hits(self):
        """Copy filtered hits to clipboard."""
        filter_text = self.hitFilter.text().strip()
        regex = None
        
        if filter_text:
            try:
                regex = re.compile(filter_text, re.IGNORECASE)
            except re.error:
                regex = None
        
        # Apply filter
        filtered_rows = []
        for row in self.hits_rows:
            if regex:
                combined_text = " ".join([row[0], str(row[1]), row[2]])
                if regex.search(combined_text):
                    filtered_rows.append(row)
            else:
                filtered_rows.append(row)
        
        if not filtered_rows:
            QtWidgets.QMessageBox.information(
                self, "Kopieren", "Keine Treffer zum Kopieren."
            )
            return
        
        # Create clipboard text
        text = "\n".join(f"{f}\t{ln}\t{snippet}" for f, ln, snippet in filtered_rows)
        QtWidgets.QApplication.clipboard().setText(text)
        self.append_log(f"In Zwischenablage: {len(filtered_rows)} Zeilen\n")

    # CLI Integration Methods
    
    def _run_cli_command(self, args: List[str]):
        """Run CLI command in background process and display output."""
        try:
            # Start CLI command as subprocess
            cmd = [sys.executable, "-m", "wallet_scanner.cli.cli_main"] + args
            
            self.cli_output.appendPlainText(f"$ wallet-scanner {' '.join(args)}\n")
            
            # Create and start process
            self.cli_proc = QtCore.QProcess(self)
            self.cli_proc.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
            self.cli_proc.readyReadStandardOutput.connect(self._on_cli_output)
            self.cli_proc.finished.connect(self._on_cli_finished)
            
            self.cli_proc.start(cmd[0], cmd[1:])
            
            # Switch to CLI tab to show result
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "CLI Tools":
                    self.tabs.setCurrentIndex(i)
                    break
                    
        except Exception as e:
            self.cli_output.appendPlainText(f"❌ Fehler beim Starten: {str(e)}\n")
    
    def _on_cli_output(self):
        """Handle CLI process output."""
        if hasattr(self, 'cli_proc') and self.cli_proc:
            data = self.cli_proc.readAllStandardOutput().data().decode('utf-8')
            self.cli_output.insertPlainText(data)
            # Auto-scroll to bottom
            cursor = self.cli_output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.cli_output.setTextCursor(cursor)
    
    def _on_cli_finished(self, exit_code: int):
        """Handle CLI process completion."""
        if exit_code == 0:
            self.cli_output.appendPlainText("✅ Befehl erfolgreich abgeschlossen\n")
        else:
            self.cli_output.appendPlainText(f"❌ Befehl beendet mit Exit-Code: {exit_code}\n")
        
        self.cli_output.appendPlainText("─" * 60 + "\n")
        self.cli_proc = None

    def run_cli_check(self):
        """Run CLI system check command."""
        self.cli_output.appendPlainText("🔍 Führe System-Check aus...\n")
        self._run_cli_command(["check"])

    def run_cli_setup(self):
        """Run CLI setup command."""
        self.cli_output.appendPlainText("⚙️ Führe Setup aus...\n")
        self._run_cli_command(["setup"])

    def run_cli_list_scanners(self):
        """Run CLI list-scanners command."""
        self.cli_output.appendPlainText("📝 Lade Scanner-Liste...\n")
        self._run_cli_command(["list-scanners"])

    def run_cli_analyze(self):
        """Run CLI analyze command on specified path."""
        path = self.analyze_path.text().strip()
        if not path:
            QtWidgets.QMessageBox.warning(self, "Fehler", "Bitte Pfad für Analyse eingeben.")
            return
            
        self.cli_output.appendPlainText(f"🔬 Analysiere Pfad: {path}\n")
        self._run_cli_command(["analyze", path])