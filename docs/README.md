# Wallet GUI & Scanner (Fedora/KDE friendly)

## Inhalte
- `wallet_gui.py` – PyQt6-GUI zum Auswählen von Ordnern/Images/Devices, Scan starten, Live-Logs & Ergebnisse
- `scripts/wallet_harvest_any.sh` – universeller Scanner für Ordner/Images/Devices, optional mit Symlink-Staging
- `install_wallet_gui.sh` – Installer (User-Scope, kein Root nötig)
- `README.md` – diese Datei

## Installation
```bash
unzip wallet-gui.zip -d wallet-gui
cd wallet-gui
chmod +x install_wallet_gui.sh
./install_wallet_gui.sh
# Empfohlene System-Pakete (Fedora):
sudo dnf install -y python3-pyqt6 kdialog p7zip p7zip-plugins sleuthkit ntfs-3g
```

Start:
```bash
wallet-gui
```

## Hinweise
- Für Images/Devices kann die GUI den Scanner via `pkexec` als Root starten (Häkchen „Mit Root“).
- Ergebnisse liegen unter `ROOT/_logs/walletscan_<timestamp>/` (Hits, Mnemonics, Kandidaten, Log).
- „Staging anlegen“ erstellt Symlinks zu Treffern in `ROOT/Software/_staging_wallets`.
- **Images/Devices**: Der Scanner versucht read-only zu mounten (losetup -P, mount -o ro). Falls ein Format nicht erkannt wird, bitte manuell mounten und den Mountpunkt als Ordner scannen.
- Das Tool nutzt robuste CLI-Utilities (`find`, `grep`, `losetup`, `mount`, optional `sleuthkit`, `7z`). Je mehr davon installiert sind, desto besser die Abdeckung.
