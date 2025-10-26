from __future__ import annotations
from PyQt6.QtGui import QTextCursor
#!/usr/bin/env python3
# Wallet GUI – polierte Version mit Stop/Filter/Export/Auto-Load
import os, sys, re, shlex, subprocess, time, shutil, tempfile
from pathlib import Path
from typing import List, Tuple, Optional
from PyQt6 import QtWidgets, QtCore, QtGui

APP_NAME = "Wallet GUI – Scanner"
DEFAULT_HELP_HTML = """
<h1>Wallet GUI – Bedienung (Kurz)</h1>
<div class=box>
<p><b>ROOT</b>: Ausgangspfad. Buttons rechts fügen Ziele (Ordner/Dateien/Devices) in die Liste ein.
<br><b>Aggressiv</b>: mehr Dateitypen/Patterns (langsamer, gründlicher).
<br><b>Staging anlegen</b>: Symlinks der Funde unter <code>Software/_staging_wallets</code>.
<br><b>Mit Root</b>: startet Scanner via <code>pkexec</code> (für Auto-Mount/Devices).
<br><b>Auto-Mount</b>: Images/Devices automatisch read-only einhängen.</p>
</div>
<h2>Tabs</h2>
<ul>
<li><b>Live-Log</b>: Ausgaben des Scanners (Auto-Scroll, Timer/Status unten).</li>
<li><b>Hits</b>: Treffer (Datei:Zeile:Snippet) mit Regex-Filter, Öffnen/Export/Kopieren.</li>
<li><b>Mnemonics</b>: Roh-Kandidaten (12/24 Wörter).</li>
<li><b>Anleitung</b>: diese Hilfe.</li>
</ul>
"""

def quoted(s: str) -> str:
    return shlex.quote(s)

class MainWindow(QtWidgets.QMainWindow):
    proc: Optional[QtCore.QProcess] = None
    last_out: Optional[Path] = None
    hits_rows: List[Tuple[str,int,str]] = []
    start_ts: float = 0.0
    timer: Optional[QtCore.QTimer] = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1050, 650)
        cw = QtWidgets.QWidget(); self.setCentralWidget(cw)
        v = QtWidgets.QVBoxLayout(cw); v.setContentsMargins(8,8,8,8); v.setSpacing(6)

        # Zeile: ROOT + Scanner
        top = QtWidgets.QHBoxLayout()
        self.rootEdit = QtWidgets.QLineEdit(str(Path("/run/media/emil/DATEN")))
        self.btnRoot = QtWidgets.QPushButton("ROOT wählen…")
        self.btnRoot.clicked.connect(self.choose_root)
        
        # Scanner-Auswahl mit Dropdown
        self.scannerCombo = QtWidgets.QComboBox()
        self.populate_scanner_list()
        self.scannerCombo.currentTextChanged.connect(self.on_scanner_changed)
        
        self.btnScanner = QtWidgets.QPushButton("Eigener Scanner…")
        self.btnScanner.clicked.connect(self.choose_scanner)
        
        top.addWidget(QtWidgets.QLabel("ROOT:"))
        top.addWidget(self.rootEdit, 1)
        top.addWidget(self.btnRoot)
        top.addWidget(QtWidgets.QLabel("Scanner:"))
        top.addWidget(self.scannerCombo, 2)
        top.addWidget(self.btnScanner)
        v.addLayout(top)

        # Ziele-Liste + Buttons rechts
        mid = QtWidgets.QHBoxLayout()
        self.targets = QtWidgets.QListWidget()
        self.targets.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        mid.addWidget(self.targets, 1)
        side = QtWidgets.QVBoxLayout()
        for text, fn in [
            ("Ordner hinzufügen", self.add_dir),
            ("Datei/Abbild hinzufügen", self.add_file),
            ("Device (/dev/…) hinzufügen", self.add_dev),
            ("Auswahl entfernen", self.rm_selected),
            ("Liste leeren", self.targets.clear),
        ]:
            b = QtWidgets.QPushButton(text); b.clicked.connect(fn); side.addWidget(b)
        side.addStretch(1)
        mid.addLayout(side)
        v.addLayout(mid, 1)

        # Optionen + Start/Stop
        opts = QtWidgets.QHBoxLayout()
        self.chkAgg = QtWidgets.QCheckBox("Aggressiv")
        self.chkStage = QtWidgets.QCheckBox("Staging anlegen (Symlinks)")
        self.chkRoot = QtWidgets.QCheckBox("Mit Root (pkexec) für Auto-Mount")
        self.chkAutoMount = QtWidgets.QCheckBox("Auto-Mount für Images/Devices"); self.chkAutoMount.setChecked(True)
        for w in (self.chkAgg, self.chkStage, self.chkRoot, self.chkAutoMount): opts.addWidget(w)
        opts.addStretch(1)
        self.btnScan = QtWidgets.QPushButton("Scan starten"); self.btnScan.clicked.connect(self.start_scan)
        self.btnStop = QtWidgets.QPushButton("Stop"); self.btnStop.setEnabled(False); self.btnStop.clicked.connect(self.stop_scan)
        opts.addWidget(self.btnScan); opts.addWidget(self.btnStop)
        v.addLayout(opts)
        
        # Zweite Optionen-Zeile
        opts2 = QtWidgets.QHBoxLayout()
        self.chkShowTerminal = QtWidgets.QCheckBox("🖥️ Terminal-Fenster beim Scan zeigen")
        self.chkShowTerminal.setToolTip("Öffnet externes Terminal mit Live-Scanner-Output\nNützlich für Debugging und Transparenz")
        opts2.addWidget(self.chkShowTerminal)
        opts2.addStretch(1)
        v.addLayout(opts2)

        # Utility-Buttons (Hilfe-Button entfernt - siehe Anleitung-Tab)
        util = QtWidgets.QHBoxLayout()
        bRoot = QtWidgets.QPushButton("ROOT in Dolphin"); bRoot.clicked.connect(lambda: self.open_path(self.rootEdit.text()))
        bStage = QtWidgets.QPushButton("Staging öffnen"); bStage.clicked.connect(lambda: self.open_path(str(Path(self.rootEdit.text())/"Software/_staging_wallets")))
        bLogs  = QtWidgets.QPushButton("Logs öffnen");   bLogs.clicked.connect(self.open_logs)
        for b in (bRoot,bStage,bLogs): util.addWidget(b)
        util.addStretch(1); v.addLayout(util)

        # Tabs
        self.tabs = QtWidgets.QTabWidget(); v.addWidget(self.tabs, 5)

        # Live-Log
        live_box = QtWidgets.QWidget(); live_v = QtWidgets.QVBoxLayout(live_box); live_v.setContentsMargins(6,6,6,6)
        self.logView = QtWidgets.QPlainTextEdit(); self.logView.setReadOnly(True)
        self.logView.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        live_v.addWidget(self.logView, 1)
        self.statusLbl = QtWidgets.QLabel("Bereit"); live_v.addWidget(self.statusLbl, 0)
        self.tabs.addTab(live_box, "Live-Log")

        # Hits
        hits_box = QtWidgets.QWidget(); hv = QtWidgets.QVBoxLayout(hits_box); hv.setContentsMargins(6,6,6,6)
        fl = QtWidgets.QHBoxLayout()
        self.hitFilter = QtWidgets.QLineEdit(); self.hitFilter.setPlaceholderText("Filter (Regex, z. B. bc1|0x|xpub|wallet\\.dat)")
        self.hitFilter.textChanged.connect(self.refresh_hits_table)
        self.btnOpenSel = QtWidgets.QPushButton("Öffnen"); self.btnOpenSel.clicked.connect(self.open_selected_hit)
        self.btnExport  = QtWidgets.QPushButton("Export .tsv"); self.btnExport.clicked.connect(self.export_hits)
        self.btnCopy    = QtWidgets.QPushButton("Kopieren"); self.btnCopy.clicked.connect(self.copy_hits)
        for w in (self.hitFilter, self.btnOpenSel, self.btnExport, self.btnCopy): fl.addWidget(w)
        fl.addStretch(1); hv.addLayout(fl)
        self.hitTable = QtWidgets.QTableWidget(0,3)
        self.hitTable.setHorizontalHeaderLabels(["Datei","Zeile","Treffer-Snippet"])
        self.hitTable.horizontalHeader().setStretchLastSection(True)
        self.hitTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.hitTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        hv.addWidget(self.hitTable,1)
        self.tabs.addTab(hits_box,"Hits")

        # Mnemonics
        self.mnemoView = QtWidgets.QPlainTextEdit(); self.mnemoView.setReadOnly(True)
        self.tabs.addTab(self.mnemoView,"Mnemonics")

        # Anleitung (Ausführliche Text-Version)
        self.helpView = QtWidgets.QPlainTextEdit()
        self.helpView.setReadOnly(True)
        self.helpView.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Setze ausführliche Anleitung
        help_text = """
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

🔹 Eigener Scanner... [Button]
   Fügt custom Scanner-Skript hinzu
   • Öffnet Dialog in ~/.local/share/wallet-gui/scripts/
   • Nur .sh und .py Dateien
   • Warnt vor standalone/-Scanner (nicht GUI-kompatibel!)

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
   
   Scanner-Verhalten:
     → Rekursive Datei-Enumeration
     → Alle Dateien ≤ 512 MB werden gescannt
     → Große Dateien (> 512 MB) werden ÜBERSPRUNGEN!
   
   Wann nutzen:
     ✅ Normale Ordner mit vielen Dateien
     ✅ /home/user/Documents/
     ✅ Gemountete Verzeichnisse
   
   NICHT für:
     ❌ Große Image-Dateien → Nutze "Datei/Abbild hinzufügen"!

🔹 Datei/Abbild hinzufügen [Button] ⭐ WICHTIG!
   Fügt Datei(en) zur Scan-Liste hinzu
   
   Was passiert:
     • Öffnet kdialog mit Multi-Selektion
     • Filter: *.img, *.iso, *.zip, *.7z, *.tar, etc.
     • Zeigt Dateigröße im Log
   
   Scanner-Verhalten (UNTERSCHIEDLICH je nach Typ!):
     → Images (.img, .iso, .dd, .raw, etc.):
        ✓ Werden read-only GEMOUNTET (braucht Root!)
        ✓ INHALT wird gescannt (nicht die Datei selbst!)
        ✓ Automatisches Unmount nach Scan
     
     → Archive (.zip, .7z, .tar, etc.):
        ✓ Werden nach /tmp/ EXTRAHIERT
        ✓ INHALT wird gescannt
        ✓ Automatisches Cleanup
     
     → Reguläre Dateien:
        ✓ Content-Scan (wenn ≤ 512 MB)
        ❌ Übersprungen wenn zu groß!
   
   ⚡ FÜR GROSSE IMAGES (> 512 MB):
      IMMER diesen Button nutzen + "Mit Root" + "Auto-Mount"!
   
   Beispiel: 233 GB .img Datei
     ❌ FALSCH: Ordner hinzufügen → .img wird übersprungen!
     ✅ RICHTIG: Datei hinzufügen + Root + Auto-Mount → Image wird gemountet!

🔹 Device (/dev/...) hinzufügen [Button]
   Fügt Block-Device zur Scan-Liste hinzu
   
   Was passiert:
     • Öffnet kdialog in /dev/disk/by-label/ (empfohlen!)
     • Multi-Selektion möglich
     • Warnt wenn Root-Rechte fehlen
   
   Scanner-Verhalten:
     → Device wird read-only GEMOUNTET
     → Mount-Punkt wird rekursiv gescannt
     → Automatisches Unmount nach Scan
   
   Wann nutzen:
     • USB-Sticks: /dev/disk/by-label/USB_BACKUP
     • Externe HDDs: /dev/disk/by-label/FORENSICS
     • Partitionen: /dev/sda1, /dev/nvme0n1p2
   
   ⚠️ WICHTIG:
      "Mit Root (pkexec)" MUSS aktiviert sein!
      "Auto-Mount" MUSS aktiviert sein!

🔹 Auswahl entfernen [Button]
   Entfernt gewählte Targets aus Liste
   • Keine Bestätigung (direkt gelöscht)
   • Multi-Selektion möglich

🔹 Liste leeren [Button]
   Löscht ALLE Targets aus Liste
   • Keine Bestätigung (direkt gelöscht)
   • Für Neustart oder Fehlerkorrektur

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
   
   Nachteile:
     ⚠ Langsamer (mehr Dateien werden gescannt)
     ⚠ Mehr RAM-Verbrauch
     ⚠ Höhere CPU-Last
   
   Wann aktivieren:
     ✅ Gründlicher Scan gewünscht
     ✅ Zeit spielt keine Rolle
     ✅ Wichtige/verdächtige Daten
   
   Wann NICHT:
     ❌ Schneller Probe-Scan
     ❌ Schwache Hardware (< 8 GB RAM)
     ❌ Sehr große Datenmengen (> 1 TB)

☐ Staging anlegen (Symlinks)
   Erstellt Symlinks aller Treffer
   
   Was passiert:
     → Scanner erstellt: <ROOT>/Software/_staging_wallets/
     → Für jeden Treffer: Symlink zur Original-Datei
     → Format: _staging_wallets/<filename>_<hash>
   
   Vorteile:
     ✓ Schneller Zugriff auf alle Funde
     ✓ Original-Dateien bleiben unverändert
     ✓ Einfach zu durchsuchen
   
   Wann aktivieren:
     ✅ Viele Treffer erwartet
     ✅ Manuelle Nachbearbeitung geplant
     ✅ Zum Sammeln von Fundstellen

☐ Mit Root (pkexec) für Auto-Mount ⚠️ WICHTIG!
   Scanner mit Root-Rechten ausführen
   
   Was ermöglicht das:
     ✓ Images mounten (losetup, mount)
     ✓ Devices mounten (/dev/sdX)
     ✓ Archive mit privilegierten Rechten entpacken
     ✓ Zugriff auf geschützte Dateien
   
   Was passiert:
     → pkexec-Passwort-Dialog erscheint beim Start
     → Scanner läuft mit sudo-Rechten
     → Cleanup läuft auch mit Root
   
   Wann AKTIVIEREN:
     ✅ Images scannen (.img, .iso, .dd)
     ✅ Devices scannen (/dev/sdX)
     ✅ Auto-Mount nutzen
   
   Wann NICHT:
     ❌ Nur normale Ordner scannen
     ❌ Bereits gemountete Verzeichnisse
     ❌ Sicherheitsbedenken

☑ Auto-Mount für Images/Devices ⚠️ WICHTIG!
   Automatisches Mounten von Images/Devices
   (Standard: AKTIVIERT)
   
   Was passiert:
     → Images (.img, .iso, .dd): Read-only mounten
     → Archive (.zip, .7z, .tar): Extrahieren
     → Devices (/dev/sdX): Read-only mounten
     → Nach Scan: Automatisches Unmount/Cleanup
   
   Ohne Auto-Mount:
     ❌ Images werden als Datei gescannt (sinnlos bei 233 GB!)
     ❌ Devices können nicht gescannt werden
     ❌ Archive werden nicht entpackt
   
   Wann AKTIVIEREN:
     ✅ IMMER bei Images/Devices! (Standard)
     ✅ Bei Archive-Scanning
   
   Wann DEAKTIVIEREN:
     ❌ Nur bei bereits gemounteten Verzeichnissen
     ❌ Wenn nur reguläre Dateien gescannt werden

═══════════════════════════════════════════════════════════════════════════════
 🔵 UTILITY-BUTTONS (Untere Zeile)
═══════════════════════════════════════════════════════════════════════════════

🔹 ROOT in Dolphin [Button]
   Öffnet ROOT-Verzeichnis im Dateimanager
   • Schneller Zugriff auf Output-Ordner
   • Vor/Nach Scan zur Kontrolle

🔹 Staging öffnen [Button]
   Öffnet Staging-Ordner im Dateimanager
   • Zeigt alle Symlinks zu Treffern
   • Nur sinnvoll wenn "Staging anlegen" aktiviert war!

🔹 Logs öffnen [Button]
   Öffnet letztes Scan-Output-Verzeichnis
   
   Inhalt:
     • hits.txt → Alle Treffer (Datei:Zeile:Snippet)
     • mnemonic_raw.txt → Seed-Kandidaten
     • scan.log → Scanner-Output
     • summary.json → Statistiken
   
   💡 Tipp: Nach jedem Scan hier prüfen!

═══════════════════════════════════════════════════════════════════════════════
 🚀 ACTION-BUTTONS
═══════════════════════════════════════════════════════════════════════════════

🔹 Scan starten [Button] (grün)
   Startet Scanner-Prozess
   
   Was passiert:
     1. Prüft ob Targets vorhanden
     2. Erstellt Output-Verzeichnis
     3. Startet Scanner (evtl. mit pkexec)
     4. Zeigt Live-Output im "Live-Log" Tab
     5. Auto-Load von Ergebnissen nach Scan
   
   Workflow:
     → Targets hinzufügen
     → Optionen wählen
     → "Scan starten" klicken
     → Im "Live-Log" Tab zuschauen
     → Warten...
     → "Hits" Tab prüfen!

🔹 Stop [Button] (rot, während Scan aktiv)
   Bricht laufenden Scan ab
   
   Was passiert:
     → Sendet SIGTERM an Scanner-Prozess
     → Cleanup wird ausgeführt
     → Partial Ergebnisse bleiben erhalten
   
   Wann nutzen:
     • Scan dauert zu lange
     • Falsche Targets gewählt
     • System überlastet

═══════════════════════════════════════════════════════════════════════════════
 📊 TABS (Ergebnisse & Info)
═══════════════════════════════════════════════════════════════════════════════

🔹 Live-Log Tab
   Scanner-Output in Echtzeit
   
   Inhalt:
     • Scanner-Meldungen
     • Fortschritt
     • Fehler/Warnungen
     • Mount/Unmount-Aktionen
   
   Features:
     ✓ Auto-Scroll (scrollt automatisch mit)
     ✓ Timer unten (Elapsed-Zeit)
     ✓ Status-Label ("Bereit", "Läuft...", "Fertig")

🔹 Hits Tab
   Gefundene Treffer anzeigen
   
   Inhalt:
     • Tabelle: Datei | Zeile | Treffer-Snippet
     • Sortierbar nach Spalten
     • Filterable mit Regex
   
   Features:
     ✓ Regex-Filter: bc1|0x|xpub|wallet\\.dat
     ✓ "Öffnen" Button → Datei im Editor öffnen
     ✓ "Export .tsv" → Alle Treffer exportieren
     ✓ "Kopieren" → Treffer in Zwischenablage

🔹 Mnemonics Tab
   Seed-Phrase-Kandidaten anzeigen
   
   Inhalt:
     • 12/24 Wort-Kombinationen
     • Heuristische Erkennung
     • Format: # Datei: /path/to/file
               word1 word2 word3 ... word12

🔹 Anleitung Tab
   Diese Hilfe
   • Komplette Bedienungsanleitung
   • Alle Buttons erklärt
   • Workflow-Tipps

═══════════════════════════════════════════════════════════════════════════════
 🎯 WORKFLOW-BEISPIEL: 233 GB IMAGE-DATEI SCANNEN
═══════════════════════════════════════════════════════════════════════════════

Situation: Du hast eine große Image-Datei (z.B. 233 GB .img)

❌ FALSCH (Image wird übersprungen!):
   1. "Ordner hinzufügen" klicken
   2. Ordner mit .img Datei wählen
   3. Scan starten
   → Image wird NICHT gescannt (zu groß > 512 MB!)

✅ RICHTIG (Image-Inhalt wird gescannt!):
   1. Scanner: "hrm_swarm_scanner_wrapper.sh" wählen
   2. "Datei/Abbild hinzufügen" klicken
   3. volume_disk_2025-10-06-1346.img auswählen
   4. ☑ "Mit Root (pkexec)" aktivieren
   5. ☑ "Auto-Mount" aktivieren
   6. Optional: ☐ "Aggressiv" für gründlicheren Scan
   7. "Scan starten" klicken
   8. Passwort eingeben (pkexec-Dialog)
   9. Im "Live-Log" Tab zuschauen
   10. Nach Scan: "Hits" Tab prüfen!
   
   → Image wird gemountet, Inhalt wird gescannt, Auto-Cleanup!

═══════════════════════════════════════════════════════════════════════════════
 🔧 DATEIGRÖSSEN-LIMITS
═══════════════════════════════════════════════════════════════════════════════

Normal-Modus:
  Max. Dateigröße: 512 MB
  → Dateien > 512 MB werden ÜBERSPRUNGEN

Aggressiv-Modus:
  Max. Dateigröße: 1024 MB (1 GB)
  → Dateien > 1 GB werden ÜBERSPRUNGEN

ABER: Images/Archive haben KEIN Limit!
  → Sie werden gemountet/extrahiert, nicht content-gescannt
  → 233 GB .img? Kein Problem mit Auto-Mount!

═══════════════════════════════════════════════════════════════════════════════
 📋 WELCHE DATEITYPEN WERDEN GESCANNT?
═══════════════════════════════════════════════════════════════════════════════

Content-Scan (Text-Suche):
  ✅ ALLE Dateien ohne Extension-Filter!
  ✅ .txt, .bin, .json, .xml, .html, .js, .py, .log, .conf, .ini
  ✅ Dateien OHNE Extension
  ✅ Binärdateien (mit -a Flag)
  
  ABER: Nur wenn Dateigröße ≤ Limit!

Auto-Mount/Extract:
  ✅ Images: .img, .iso, .dd, .raw, .dmg, .vhd, .vhdx, .vmdk
  ✅ Archive: .zip, .7z, .tar, .tar.gz, .tgz, .tar.xz, .rar
  ✅ Devices: /dev/sdX, /dev/nvme0n1pX, /dev/mmcblkXpX
  
  Kein Größenlimit für Auto-Mount!

═══════════════════════════════════════════════════════════════════════════════
 💡 TIPPS & TRICKS
═══════════════════════════════════════════════════════════════════════════════

🔹 Für große Images:
   • IMMER "Datei/Abbild hinzufügen" nutzen (nicht Ordner!)
   • Root + Auto-Mount aktivieren
   • Scanner: hrm_swarm_scanner_wrapper.sh

🔹 Für Devices (/dev/sdX):
   • /dev/disk/by-label/ nutzen (lesbare Namen!)
   • Root + Auto-Mount MUSS aktiviert sein
   • Read-only Mount (sicher)

🔹 Für Archive:
   • Mehrere Archive mit Strg+Klick wählen
   • Werden automatisch entpackt
   • Temporäre Dateien in /tmp/

🔹 Performance:
   • ROOT auf schneller SSD
   • Aggressiv-Modus nur bei Bedarf
   • Bei vielen CPUs: Threads erhöhen

🔹 Nach dem Scan:
   • "Hits" Tab prüfen
   • "Logs öffnen" für Details
   • hits.txt für manuelle Analyse

═══════════════════════════════════════════════════════════════════════════════
 📦 EMPFOHLENE PAKETE
═══════════════════════════════════════════════════════════════════════════════

Erforderlich:
  • python3-pyqt6 → GUI-Framework
  • kdialog → Native KDE-Dialoge (besser als Qt!)

Für Auto-Mount:
  • p7zip, p7zip-plugins → Archive (.7z, .zip)
  • tar, gzip, xz, bzip2 → Archive (.tar.*)

Forensik:
  • sleuthkit → Image-Analyse
  • ntfs-3g → NTFS-Support
  • exfatprogs → exFAT-Support

Scanner:
  • ripgrep → Schnelle Text-Suche (optional)
  • yara → Pattern-Matching (optional)

═══════════════════════════════════════════════════════════════════════════════
 ✅ ZUSAMMENFASSUNG
═══════════════════════════════════════════════════════════════════════════════

1. ROOT setzen (wo Ergebnisse gespeichert werden)
2. Scanner wählen (hrm_swarm_scanner_wrapper.sh empfohlen!)
3. Targets hinzufügen:
   • Ordner → für normale Dateien
   • Datei → für Images/Archive (WICHTIG bei großen Files!)
   • Device → für USB-Sticks/HDDs
4. Optionen wählen:
   • Root + Auto-Mount für Images/Devices
   • Aggressiv für gründlichen Scan
5. "Scan starten" klicken
6. "Live-Log" beobachten
7. "Hits" Tab prüfen!

═══════════════════════════════════════════════════════════════════════════════
        """
        
        self.helpView.setPlainText(help_text)
        self.tabs.addTab(self.helpView,"Anleitung")

        self.append_log("Hinweis: Empfohlene Pakete: python3-pyqt6 kdialog p7zip p7zip-plugins sleuthkit ntfs-3g\n")

    # -- helpers --
    def populate_scanner_list(self):
        """Befüllt die Scanner-Dropdown-Liste mit verfügbaren Scannern aus scripts/"""
        scripts_dir = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
        
        scanners = []
        if scripts_dir.exists():
            # Sammle alle .sh und .py Dateien
            for pattern in ("*.sh", "*.py"):
                scanners.extend(scripts_dir.glob(pattern))
        
        # Sortiere nach Name
        scanners.sort(key=lambda p: p.name)
        
        # Standard-Scanner
        default_scanner = scripts_dir / "wallet_harvest_any.sh"
        
        self.scannerCombo.clear()
        for s in scanners:
            # Zeige nur den Dateinamen im Dropdown
            display_name = s.name
            # Speichere den vollen Pfad als userData
            self.scannerCombo.addItem(display_name, str(s))
        
        # Setze Standard-Scanner
        if default_scanner.exists():
            idx = self.scannerCombo.findData(str(default_scanner))
            if idx >= 0:
                self.scannerCombo.setCurrentIndex(idx)
    
    def on_scanner_changed(self, text: str):
        """Wird aufgerufen wenn ein Scanner aus dem Dropdown gewählt wird"""
        # Der aktuelle Pfad ist in userData gespeichert
        pass
    
    def get_current_scanner(self) -> str:
        """Gibt den Pfad des aktuell gewählten Scanners zurück"""
        return self.scannerCombo.currentData() or ""
    
    def run_fsearch_dialog(self, title: str, initial_path: str, mode: str = "file") -> Optional[str]:
        """
        Öffnet FSearch und lässt User eine Datei/Ordner wählen
        
        Args:
            title: Dialog-Titel (wird als Hinweis im Log gezeigt)
            initial_path: Startpfad für FSearch
            mode: "file" oder "directory"
        
        Returns:
            Gewählter Pfad oder None
        """
        self.append_log(f"🔍 FSearch öffnen: {title}\n")
        self.append_log(f"   Startpfad: {initial_path}\n")
        if mode == "directory":
            self.append_log(f"   💡 Tipp: Doppelklick auf Ordner um auszuwählen\n")
        else:
            self.append_log(f"   💡 Tipp: Doppelklick auf Datei um auszuwählen\n")
        
        # Erstelle temporäre Datei für Auswahl
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            selection_file = f.name
        
        try:
            # Starte FSearch mit initial path
            # FSearch nutzt GTK und blockiert nicht, daher nutzen wir ein Wrapper-Skript
            wrapper_script = f"""#!/bin/bash
fsearch --path "{initial_path}"
# Warte auf Auswahl - User muss Datei/Ordner in Zwischenablage kopieren und Enter drücken
echo "FSearch geöffnet. Bitte:"
echo "1. Datei/Ordner auswählen"
echo "2. Mit Strg+C in Zwischenablage kopieren"
echo "3. Dieses Terminal-Fenster fokussieren"
echo "4. Enter drücken"
read -r selection
if [ -n "$selection" ]; then
    echo "$selection" > "{selection_file}"
fi
"""
            # Einfachere Lösung: Nutze kdialog wenn verfügbar
            if shutil.which("kdialog"):
                if mode == "directory":
                    result = subprocess.run(
                        ["kdialog", "--title", title, "--getexistingdirectory", initial_path],
                        capture_output=True, text=True
                    )
                else:
                    result = subprocess.run(
                        ["kdialog", "--title", title, "--getopenfilename", initial_path],
                        capture_output=True, text=True
                    )
                
                if result.returncode == 0 and result.stdout.strip():
                    selected = result.stdout.strip()
                    self.append_log(f"✓ Ausgewählt: {selected}\n")
                    return selected
                else:
                    self.append_log("✗ Abgebrochen\n")
                    return None
            else:
                # Starte FSearch im Hintergrund
                subprocess.Popen(["fsearch", "--path", initial_path])
                
                # Zeige Dialog für manuelle Eingabe
                text, ok = QtWidgets.QInputDialog.getText(
                    self,
                    title,
                    f"FSearch geöffnet!\n\nBitte Pfad eingeben oder aus FSearch kopieren:\n(Startpfad: {initial_path})",
                    QtWidgets.QLineEdit.EchoMode.Normal,
                    initial_path
                )
                
                if ok and text:
                    self.append_log(f"✓ Ausgewählt: {text}\n")
                    return text
                else:
                    self.append_log("✗ Abgebrochen\n")
                    return None
        
        finally:
            # Cleanup
            try:
                Path(selection_file).unlink()
            except:
                pass
    
    def append_log(self, text: str):
        self.logView.appendPlainText(text.rstrip("\n"))
        self.logView.moveCursor(QTextCursor.MoveOperation.End)

    def choose_root(self):
        """Wähle ROOT-Verzeichnis mit FSearch"""
        # Nutze FSearch wenn verfügbar, sonst Qt-Dialog
        if shutil.which("fsearch"):
            initial = self.rootEdit.text() or "/run/media"
            result = self.run_fsearch_dialog(
                title="ROOT-Verzeichnis auswählen",
                initial_path=initial,
                mode="directory"
            )
            if result:
                self.rootEdit.setText(result)
                self.append_log(f"✓ ROOT gesetzt: {result}\n")
        else:
            # Fallback: Qt-Dialog
            dialog = QtWidgets.QFileDialog(self)
            dialog.setWindowTitle("ROOT-Verzeichnis auswählen")
            dialog.setDirectory(self.rootEdit.text() or "/")
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
            dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
            dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
            dialog.resize(1200, 800)
            
            if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
                d = dialog.selectedFiles()[0]
                if d: self.rootEdit.setText(d)

    def choose_scanner(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Scanner-Skript wählen")
        
        # Setze das Verzeichnis auf scripts/ (nicht standalone/)
        scripts_dir = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
        if scripts_dir.exists():
            dialog.setDirectory(str(scripts_dir))
        else:
            dialog.setDirectory(str(Path.home()))
        
        dialog.setNameFilter("Shell-Skripte (*.sh);;Python-Skripte (*.py);;Alle Dateien (*)")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        
        # PROFESSIONELLE GRÖSSE
        dialog.resize(1200, 800)
        
        # Shortcuts
        shortcuts = [
            QtCore.QUrl.fromLocalFile(str(scripts_dir)),
            QtCore.QUrl.fromLocalFile(str(Path.home() / ".local" / "share" / "wallet-gui")),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        # Info-Label für Benutzer
        info = QtWidgets.QLabel(
            "💡 <b>Hinweis:</b> Bitte nur Scanner aus dem <code>scripts/</code> Ordner wählen.<br>"
            "⚠️ <b>Standalone-Scanner</b> (<code>standalone/</code>) sind <b>NICHT GUI-kompatibel</b> "
            "und müssen per CLI gestartet werden."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { background-color: #fff3cd; padding: 8px; margin: 4px; border: 1px solid #ffc107; }")
        
        # Füge Info-Label zum Dialog hinzu
        layout = dialog.layout()
        if layout:
            layout.addWidget(info, 0, 0, 1, -1)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            f = dialog.selectedFiles()[0]
            if f:
                # Warne wenn standalone/ gewählt wurde
                if "standalone" in f:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Warnung: Standalone-Scanner",
                        f"Der gewählte Scanner ist ein Standalone-Scanner:\n{f}\n\n"
                        "Standalone-Scanner sind NICHT GUI-kompatibel und müssen direkt\n"
                        "über die Kommandozeile ausgeführt werden.\n\n"
                        "Bitte wählen Sie einen Scanner aus dem scripts/ Ordner."
                    )
                    return
                # Füge custom Scanner zur Combo-Box hinzu
                display_name = f"⭐ {Path(f).name}"
                self.scannerCombo.addItem(display_name, f)
                self.scannerCombo.setCurrentIndex(self.scannerCombo.count() - 1)
                self.append_log(f"✓ Custom-Scanner gewählt: {Path(f).name}\n")

    def add_dir(self):
        """Füge Ordner zur Scan-Liste hinzu (mit FSearch/kdialog)"""
        if shutil.which("kdialog"):
            # Nutze kdialog - unterstützt Multi-Selektion
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
        
        # Fallback: Qt-Dialog
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Ordner hinzufügen (Mehrfachauswahl möglich)")
        dialog.setDirectory(self.rootEdit.text() or "/")
        
        # WICHTIG: Directory-Mode aber OHNE ShowDirsOnly damit Dateien sichtbar sind!
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setOption(QtWidgets.QFileDialog.Option.ShowDirsOnly, False)  # Zeige auch Dateien!
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        
        # PROFESSIONELLE GRÖSSE + MULTI-SELEKTION
        dialog.resize(1200, 800)
        
        # Shortcuts für schnellen Zugriff
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/"),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
            QtCore.QUrl.fromLocalFile("/run/media"),
            QtCore.QUrl.fromLocalFile("/mnt"),
            QtCore.QUrl.fromLocalFile("/media"),
            QtCore.QUrl.fromLocalFile("/dev"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        # Info-Label
        info = QtWidgets.QLabel(
            "💡 <b>Tipp:</b> Sie können mehrere Ordner auf einmal auswählen mit <b>Strg+Klick</b> oder <b>Shift+Klick</b>"
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { background-color: #e3f2fd; padding: 6px; margin: 4px; }")
        layout = dialog.layout()
        if layout:
            layout.addWidget(info, 0, 0, 1, -1)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for d in dialog.selectedFiles():
                if d and not self.targets.findItems(d, QtCore.Qt.MatchFlag.MatchExactly):
                    self.targets.addItem(d)
                    self.append_log(f"✓ Ziel hinzugefügt: {d}\n")

    def add_file(self):
        """Füge Dateien/Images zur Scan-Liste hinzu (mit kdialog)"""
        if shutil.which("kdialog"):
            # Nutze kdialog - unterstützt Multi-Selektion und Filter
            initial = self.rootEdit.text() or "/run/media"
            
            # Filter für kdialog
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
                        size_mb = size / (1024*1024)
                        self.targets.addItem(path)
                        self.append_log(f"✓ Datei hinzugefügt: {path} ({size_mb:.1f} MB)\n")
                return
        
        # Fallback: Qt-Dialog
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Datei/Abbild hinzufügen (Mehrfachauswahl möglich)")
        dialog.setDirectory(self.rootEdit.text() or "/")
        
        # Filter mit Alle Dateien als STANDARD
        dialog.setNameFilter("Alle Dateien (*);;Disk-Images (*.img *.IMG *.iso *.ISO *.dd *.DD *.raw *.RAW *.vhd *.vhdx *.vmdk *.qcow2);;Archive (*.zip *.ZIP *.rar *.RAR *.7z *.7Z *.tar *.TAR *.tar.gz *.tgz *.TGZ)")
        dialog.selectNameFilter("Alle Dateien (*)")  # Standard: ALLE anzeigen!
        
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # MEHRFACHAUSWAHL!
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        
        # PROFESSIONELLE GRÖSSE
        dialog.resize(1200, 800)
        
        # Shortcuts
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/"),
            QtCore.QUrl.fromLocalFile(str(Path.home())),
            QtCore.QUrl.fromLocalFile("/run/media"),
            QtCore.QUrl.fromLocalFile("/mnt"),
            QtCore.QUrl.fromLocalFile("/media"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        # Info-Label mit Dateigrößen-Hinweis
        info = QtWidgets.QLabel(
            "💡 <b>Tipp:</b> Mehrfachauswahl mit <b>Strg+Klick</b>. "
            "Unterstützt: Images (.img, .iso), Archive (.zip, .7z, .tar), etc."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { background-color: #fff3cd; padding: 6px; margin: 4px; }")
        layout = dialog.layout()
        if layout:
            layout.addWidget(info, 0, 0, 1, -1)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for f in dialog.selectedFiles():
                if f and not self.targets.findItems(f, QtCore.Qt.MatchFlag.MatchExactly):
                    size = Path(f).stat().st_size if Path(f).exists() else 0
                    size_mb = size / (1024*1024)
                    self.targets.addItem(f)
                    self.append_log(f"✓ Ziel hinzugefügt: {f} ({size_mb:.1f} MB)\n")

    def add_dev(self):
        """Füge Device zur Scan-Liste hinzu (mit kdialog)"""
        if shutil.which("kdialog"):
            # Nutze kdialog für Device-Auswahl
            # Starte in /dev/disk/by-label für bessere Übersicht
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
                
                # Prüfe ob Root-Optionen aktiviert sind
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
                return
        
        # Fallback: Qt-Dialog
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle("Device wählen (/dev/...)")
        dialog.setDirectory("/dev")
        dialog.setNameFilter("Block-Devices (sd* nvme* mmcblk* vd* hd* loop*);;Alle Dateien (*)")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # MEHRFACHAUSWAHL!
        dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        
        # PROFESSIONELLE GRÖSSE
        dialog.resize(1200, 800)
        
        # Shortcuts für Device-Zugriff
        shortcuts = [
            QtCore.QUrl.fromLocalFile("/dev"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-id"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-uuid"),
            QtCore.QUrl.fromLocalFile("/dev/disk/by-label"),
            QtCore.QUrl.fromLocalFile("/sys/block"),
        ]
        dialog.setSidebarUrls(shortcuts)
        
        # Warnungs-Info
        info = QtWidgets.QLabel(
            "⚠️ <b>ACHTUNG:</b> Device-Scanning erfordert Root-Rechte! "
            "Aktivieren Sie <b>'Mit Root (pkexec)'</b> und <b>'Auto-Mount'</b>.<br>"
            "💡 <b>Tipp:</b> In <code>/dev/disk/by-label</code> finden Sie lesbare Namen."
        )
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { background-color: #ffebee; padding: 8px; margin: 4px; border: 2px solid #f44336; }")
        layout = dialog.layout()
        if layout:
            layout.addWidget(info, 0, 0, 1, -1)
        
        if dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            for f in dialog.selectedFiles():
                if f and not self.targets.findItems(f, QtCore.Qt.MatchFlag.MatchExactly):
                    self.targets.addItem(f)
                    self.append_log(f"✓ Device hinzugefügt: {f}\n")
            
            # Prüfe ob Root-Optionen aktiviert sind
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
        for it in self.targets.selectedItems():
            self.targets.takeItem(self.targets.row(it))

    def open_path(self, p: str):
        if not p: return
        path = Path(p)
        if not path.exists():
            QtWidgets.QMessageBox.warning(self,"Öffnen","Pfad existiert nicht:\n"+p); return
        if path.is_file() and shutil.which("dolphin"):
            subprocess.Popen(["dolphin","--select",str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path if path.is_dir() else path.parent)])

    def open_logs(self):
        if self.last_out and self.last_out.exists():
            subprocess.Popen(["xdg-open", str(self.last_out)])
        else:
            subprocess.Popen(["xdg-open", str(Path(self.rootEdit.text())/"_logs")])

    # open_interactive_help entfernt - Anleitung jetzt direkt im Tab

    # -- scan --
    def start_scan(self):
        if self.proc:
            QtWidgets.QMessageBox.information(self,"Läuft","Ein Scan läuft bereits."); return
        root = self.rootEdit.text().strip()
        if not root: QtWidgets.QMessageBox.warning(self,"Fehler","ROOT ist leer."); return
        
        script = self.get_current_scanner()
        if not script or not Path(script).exists():
            QtWidgets.QMessageBox.warning(self,"Fehler","Scanner-Skript nicht gefunden:\n"+script); return

        targets = [self.targets.item(i).text() for i in range(self.targets.count())]
        if not targets:
            defaults = []
            for sub in ("_mount/hitachi_sdc3_ntfs","_recovery","Software/Collected"):
                p = Path(root)/sub
                if p.exists(): defaults.append(str(p))
            targets = defaults

        args = [script, root]
        if self.chkAgg.isChecked(): args.append("--aggressive")
        if self.chkStage.isChecked(): args.append("--staging")
        if self.chkAutoMount.isChecked(): args.append("--auto-mount")
        args.extend(targets)

        cmd = ["bash","-lc"," ".join(quoted(a) for a in args)]
        if self.chkRoot.isChecked(): cmd = ["pkexec"] + cmd

        self.append_log("\n== Starte ==\n" + " ".join(args) + "\n")
        self.last_out = None
        self.btnScan.setEnabled(False); self.btnStop.setEnabled(True)
        self.start_ts = time.time()
        self.statusLbl.setText("Läuft …")
        if self.timer: self.timer.stop()
        self.timer = QtCore.QTimer(self); self.timer.timeout.connect(self.update_elapsed); self.timer.start(500)

        # Terminal-Fenster öffnen wenn gewünscht
        if self.chkShowTerminal.isChecked():
            self.open_scanner_terminal(cmd)
        else:
            # Normaler Modus: Output in GUI
            self.proc = QtCore.QProcess(self)
            self.proc.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
            self.proc.readyReadStandardOutput.connect(self.on_proc_out)
            self.proc.finished.connect(self.on_proc_finished)
            self.proc.start(cmd[0], cmd[1:])
    
    def open_scanner_terminal(self, cmd: List[str]):
        """
        Öffnet ein externes Terminal-Fenster für den Scanner
        Unterstützt verschiedene Terminal-Emulatoren
        """
        import tempfile
        
        # Erstelle temporäres Wrapper-Script
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

# Führe Scanner aus
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
        
        # Erkenne Terminal-Emulator
        terminals = [
            # KDE
            ("konsole", ["konsole", "--hold", "-e", "bash", wrapper]),
            # GNOME
            ("gnome-terminal", ["gnome-terminal", "--wait", "--", "bash", wrapper]),
            # XFCE
            ("xfce4-terminal", ["xfce4-terminal", "--hold", "-e", f"bash {wrapper}"]),
            # Generisch
            ("xterm", ["xterm", "-hold", "-e", "bash", wrapper]),
            # Fallback
            ("x-terminal-emulator", ["x-terminal-emulator", "-e", f"bash {wrapper}; read"]),
        ]
        
        terminal_cmd = None
        for name, term_cmd in terminals:
            if shutil.which(name):
                terminal_cmd = term_cmd
                self.append_log(f"🖥️ Öffne Terminal: {name}\n")
                break
        
        if not terminal_cmd:
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
            # Starte normal ohne Terminal
            self.proc = QtCore.QProcess(self)
            self.proc.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
            self.proc.readyReadStandardOutput.connect(self.on_proc_out)
            self.proc.finished.connect(self.on_proc_finished)
            self.proc.start(cmd[0], cmd[1:])
            return
        
        # Starte Terminal
        self.proc = QtCore.QProcess(self)
        self.proc.finished.connect(self.on_proc_finished_terminal)
        self.proc.start(terminal_cmd[0], terminal_cmd[1:])
        
        # Cleanup-Timer für Wrapper-Script (nach 5 Minuten)
        QtCore.QTimer.singleShot(300000, lambda: self.cleanup_wrapper(wrapper))
    
    def cleanup_wrapper(self, wrapper: str):
        """Löscht temporäres Wrapper-Script"""
        try:
            if os.path.exists(wrapper):
                os.remove(wrapper)
        except:
            pass
    
    def on_proc_finished_terminal(self, exitCode, exitStatus):
        """Wird aufgerufen wenn Terminal-Prozess beendet wurde"""
        self.append_log("\n🖥️ Terminal-Fenster geschlossen\n")
        self.append_log("\n== Fertig ==\n")
        self.btnScan.setEnabled(True); self.btnStop.setEnabled(False)
        if self.timer: self.timer.stop()
        self.statusLbl.setText("Fertig")
        self.proc = None
        # Warte kurz und lade dann Ergebnisse
        QtCore.QTimer.singleShot(1000, self.load_results)


    def stop_scan(self):
        if not self.proc: return
        try:
            self.proc.terminate()
            if not self.proc.waitForFinished(2000):
                self.proc.kill()
        finally:
            self.proc = None
            self.btnScan.setEnabled(True); self.btnStop.setEnabled(False)
            self.statusLbl.setText("Abgebrochen")
            if self.timer: self.timer.stop()

    def update_elapsed(self):
        if not self.start_ts: return
        dt = int(time.time() - self.start_ts)
        self.statusLbl.setText(f"Läuft … {dt//3600:02d}:{(dt%3600)//60:02d}:{dt%60:02d}")

    def on_proc_out(self):
        if not self.proc: return
        data = bytes(self.proc.readAllStandardOutput()).decode(errors="ignore")
        if not data: return
        self.append_log(data)
        m = re.search(r"OUT=(\S+)", data)
        if m: self.last_out = Path(m.group(1))

    def on_proc_finished(self, exitCode, exitStatus):
        self.append_log("\n== Fertig ==\n")
        self.btnScan.setEnabled(True); self.btnStop.setEnabled(False)
        if self.timer: self.timer.stop()
        self.statusLbl.setText("Fertig")
        self.proc = None
        self.load_results()

    # -- Ergebnisse laden/anzeigen --
    def load_results(self):
        out = self.last_out
        if not out or not out.exists():
            logs = Path(self.rootEdit.text())/"_logs"
            if logs.exists():
                scans = sorted(logs.glob("walletscan_*"), key=lambda p:p.stat().st_mtime, reverse=True)
                if scans: out = scans[0]
        if not out or not out.exists(): return

        # Hits
        hits = out/"hits.txt"
        self.hits_rows = []
        if hits.exists():
            for line in hits.read_text(errors="ignore").splitlines():
                m = re.match(r"^(.*?):(\\d+):(.*)$", line)
                if m: self.hits_rows.append((m.group(1), int(m.group(2)), m.group(3).strip()))
        self.refresh_hits_table()

        # Mnemonics
        mn = out/"mnemonic_raw.txt"
        self.mnemoView.setPlainText(mn.read_text(errors="ignore") if mn.exists() else "(keine Kandidaten)")

    def refresh_hits_table(self):
        filt = self.hitFilter.text().strip()
        rx = None
        if filt:
            try: rx = re.compile(filt, re.IGNORECASE)
            except re.error: rx = None
        rows = [r for r in self.hits_rows if (rx.search(" ".join([r[0],str(r[1]),r[2]])) if rx else True)]
        t = self.hitTable
        t.setRowCount(0); t.setSortingEnabled(False)
        for f,ln,snip in rows:
            r = t.rowCount(); t.insertRow(r)
            t.setItem(r,0, QtWidgets.QTableWidgetItem(f))
            t.setItem(r,1, QtWidgets.QTableWidgetItem(str(ln)))
            t.setItem(r,2, QtWidgets.QTableWidgetItem(snip))
        t.setSortingEnabled(True); t.sortItems(0, QtCore.Qt.SortOrder.AscendingOrder)

    def selected_hit(self) -> Optional[Tuple[str,int,str]]:
        r = self.hitTable.currentRow()
        if r < 0: return None
        return (self.hitTable.item(r,0).text(),
                int(self.hitTable.item(r,1).text()),
                self.hitTable.item(r,2).text())

    def open_selected_hit(self):
        sel = self.selected_hit()
        if not sel: return
        f = Path(sel[0])
        if shutil.which("dolphin"): subprocess.Popen(["dolphin","--select",str(f)])
        else: subprocess.Popen(["xdg-open", str(f.parent)])

    def export_hits(self):
        """Treffer als TSV exportieren (unter Beachtung des Filters)."""
        import csv, re
        filt = self.hitFilter.text().strip()
        rx = None
        if filt:
            try: rx = re.compile(filt, re.IGNORECASE)
            except re.error: rx = None
        rows = [r for r in self.hits_rows
                if (rx.search(" ".join([r[0], str(r[1]), r[2]])) if rx else True)]
        if not rows:
            QtWidgets.QMessageBox.information(self, "Export", "Keine Treffer zum Exportieren.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export als TSV", "hits.tsv", "TSV (*.tsv);;Alle Dateien (*)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["file", "line", "snippet"])
            for row in rows:
                w.writerow(row)
        self.append_log(f"Exportiert: {path}\n")

    def copy_hits(self):
        """Treffer (gefiltert) in die Zwischenablage kopieren."""
        import re
        filt = self.hitFilter.text().strip()
        rx = None
        if filt:
            try: rx = re.compile(filt, re.IGNORECASE)
            except re.error: rx = None
        rows = [r for r in self.hits_rows
                if (rx.search(" ".join([r[0], str(r[1]), r[2]])) if rx else True)]
        if not rows:
            QtWidgets.QMessageBox.information(self, "Kopieren", "Keine Treffer zum Kopieren.")
            return
        txt = "\n".join(f"{f}\t{ln}\t{snip}" for f, ln, snip in rows)
        QtWidgets.QApplication.clipboard().setText(txt)
        self.append_log(f"In Zwischenablage: {len(rows)} Zeilen\n")

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
