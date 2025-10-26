# Wallet GUI - Forensischer Cryptocurrency Scanner 🔍# Wallet GUI & Scanner (Fedora/KDE friendly)



Grafische Benutzeroberfläche für systematisches Scannen von Dateisystemen, Images und Devices nach Cryptocurrency-Wallets und Seed-Phrases.## Inhalte

- `wallet_gui.py` – PyQt6-GUI zum Auswählen von Ordnern/Images/Devices, Scan starten, Live-Logs & Ergebnisse

## 🎯 Features- `scripts/wallet_harvest_any.sh` – universeller Scanner für Ordner/Images/Devices, optional mit Symlink-Staging

- `install_wallet_gui.sh` – Installer (User-Scope, kein Root nötig)

- ✅ **Multi-Target-Scanning**: Ordner, Dateien, Images (.img, .iso), Archive (.zip, .7z), Devices (/dev/sdX)- `README.md` – diese Datei

- ✅ **Auto-Mount**: Automatisches Mounten von Disk-Images und Devices (mit Root-Rechten)

- ✅ **KDE-Integration**: Native kdialog-Unterstützung für bessere Dateiauswahl## Installation

- ✅ **HRM-Scanner**: Human Reasoning Model für adaptive Scan-Strategien```bash

- ✅ **Pattern-Matching**: YARA-Integration für Wallet-Artefakteunzip wallet-gui.zip -d wallet-gui

- ✅ **Seed-Phrase-Erkennung**: Heuristische 12/24-Wort-Mnemonic-Extraktioncd wallet-gui

- ✅ **Live-Monitoring**: Echtzeit-Anzeige von Scanner-Outputchmod +x install_wallet_gui.sh

- ✅ **Export-Funktionen**: TSV-Export, Staging-Symlinks./install_wallet_gui.sh

# Empfohlene System-Pakete (Fedora):

## 📦 Installationsudo dnf install -y python3-pyqt6 kdialog p7zip p7zip-plugins sleuthkit ntfs-3g

```

### System-Dependencies (Fedora/RHEL)

```bashStart:

sudo dnf install python3-pyqt6 kdialog p7zip p7zip-plugins sleuthkit ntfs-3g ripgrep```bash

```wallet-gui

```

### System-Dependencies (Debian/Ubuntu)

```bash## Hinweise

sudo apt install python3-pyqt6 kdialog p7zip-full sleuthkit ntfs-3g ripgrep- Für Images/Devices kann die GUI den Scanner via `pkexec` als Root starten (Häkchen „Mit Root“).

```- Ergebnisse liegen unter `ROOT/_logs/walletscan_<timestamp>/` (Hits, Mnemonics, Kandidaten, Log).

- „Staging anlegen“ erstellt Symlinks zu Treffern in `ROOT/Software/_staging_wallets`.

### Python-Dependencies- **Images/Devices**: Der Scanner versucht read-only zu mounten (losetup -P, mount -o ro). Falls ein Format nicht erkannt wird, bitte manuell mounten und den Mountpunkt als Ordner scannen.

```bash- Das Tool nutzt robuste CLI-Utilities (`find`, `grep`, `losetup`, `mount`, optional `sleuthkit`, `7z`). Je mehr davon installiert sind, desto besser die Abdeckung.

pip install -r requirements.txt
```

### Installation
```bash
./install_wallet_gui.sh
```

## 🚀 Schnellstart

```bash
python3 wallet_gui.py
```

## 🧠 Was ist HRM?

**HRM = Human Reasoning Model**

Adaptiver Scanner-Controller mit dynamischer Strategie-Anpassung basierend auf Scan-Ergebnissen.

## 📂 Projektstruktur

```
wallet-gui/
├── wallet_gui.py                    # Haupt-GUI
├── requirements.txt                 # Dependencies
├── scripts/                         # GUI-Scanner
├── standalone/                      # CLI-Scanner
├── tools/                           # Utilities
└── docs/                            # Dokumentation
```

## 💡 Quick-Tipp: Große Images scannen

```bash
✅ RICHTIG: "Datei/Abbild hinzufügen" + Root + Auto-Mount
❌ FALSCH: "Ordner hinzufügen" (Image wird übersprungen!)
```

Siehe `docs/` für Details.
