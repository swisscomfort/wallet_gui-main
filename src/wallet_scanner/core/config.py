#!/usr/bin/env python3
"""
Wallet Scanner Configuration Module

This module contains application configuration constants and settings
for the Wallet Scanner application.
"""

from pathlib import Path

# Application metadata
APP_NAME = "Wallet GUI – Scanner"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Cryptocurrency Wallet Forensic Scanner"
APP_AUTHOR = "Wallet Scanner Team"

# Default paths and directories
DEFAULT_ROOT_PATH = "/run/media/emil/DATEN"
DEFAULT_SCRIPTS_DIR = Path.home() / ".local" / "share" / "wallet-gui" / "scripts"
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "wallet-scanner"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "wallet-scanner"

# Scanner configuration
DEFAULT_SCANNER = "wallet_harvest_any.sh"
RECOMMENDED_SCANNER = "hrm_swarm_scanner_wrapper.sh"

# File size limits (in bytes)
DEFAULT_FILE_SIZE_LIMIT = 512 * 1024 * 1024  # 512 MB
AGGRESSIVE_FILE_SIZE_LIMIT = 1024 * 1024 * 1024  # 1 GB

# Threading configuration
DEFAULT_THREADS = 6
AGGRESSIVE_THREADS = 10

# Supported file extensions
IMAGE_EXTENSIONS = {
    ".img", ".IMG", ".iso", ".ISO", ".dd", ".DD", ".raw", ".RAW",
    ".vhd", ".vhdx", ".vmdk", ".qcow2", ".dmg"
}

ARCHIVE_EXTENSIONS = {
    ".zip", ".ZIP", ".rar", ".RAR", ".7z", ".7Z", ".tar", ".TAR",
    ".tar.gz", ".tgz", ".TGZ", ".tar.xz", ".tar.bz2"
}

# Device patterns
DEVICE_PATTERNS = [
    "/dev/sd*", "/dev/nvme*", "/dev/mmcblk*", "/dev/vd*", "/dev/hd*", "/dev/loop*"
]

# Required system packages
REQUIRED_PACKAGES = [
    "python3-pyqt6",
    "kdialog",
    "p7zip",
    "p7zip-plugins",
    "sleuthkit",
    "ntfs-3g"
]

OPTIONAL_PACKAGES = [
    "ripgrep",
    "yara",
    "exfatprogs"
]

# File dialog configuration
DIALOG_SIZE = (1200, 800)

# Default help content for the GUI
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

# Terminal emulators (in order of preference)
TERMINAL_EMULATORS = [
    ("konsole", ["konsole", "--hold", "-e"]),
    ("gnome-terminal", ["gnome-terminal", "--wait", "--"]),
    ("xfce4-terminal", ["xfce4-terminal", "--hold", "-e"]),
    ("xterm", ["xterm", "-hold", "-e"]),
    ("x-terminal-emulator", ["x-terminal-emulator", "-e"]),
]

# File manager shortcuts for dialogs
DIALOG_SHORTCUTS = [
    "/",
    "/home",
    "/run/media",
    "/mnt",
    "/media",
    "/dev",
]

# Device-specific shortcuts
DEVICE_SHORTCUTS = [
    "/dev",
    "/dev/disk/by-id",
    "/dev/disk/by-uuid", 
    "/dev/disk/by-label",
    "/sys/block",
]