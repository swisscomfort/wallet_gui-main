#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="${HOME}/.local"
APPDIR="${PREFIX}/share/wallet-gui"
BINDIR="${PREFIX}/bin"
DESKTOPDIR="${HOME}/.local/share/applications"

mkdir -p "${APPDIR}" "${BINDIR}" "${DESKTOPDIR}"

# Dateien kopieren
rsync -a --delete "${HERE}/" "${APPDIR}/"

# Starter-Skript
cat > "${BINDIR}/wallet-gui" <<'EOF'
#!/usr/bin/env bash
exec python3 "${HOME}/.local/share/wallet-gui/wallet_gui.py" "$@"
EOF
chmod +x "${BINDIR}/wallet-gui"

# Desktop-Entry
cat > "${DESKTOPDIR}/wallet-gui.desktop" <<'EOF'
[Desktop Entry]
Name=Wallet GUI
Comment=Scan nach Wallet-Hinweisen (wallet.dat, keystore, mnemonics, xpub/xprv, etc.)
Exec=wallet-gui
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;Security;Qt;
EOF

echo "Installiert nach: ${APPDIR}"
echo "Starte mit: wallet-gui"
echo
echo "Empfohlene Abhängigkeiten (Fedora):"
echo "  sudo dnf install -y python3-pyqt6 kdialog p7zip p7zip-plugins sleuthkit ntfs-3g"
