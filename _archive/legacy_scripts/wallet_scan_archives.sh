#!/bin/bash
# wallet_scan_archives.sh
# Ergänzt dein GUI: fokussiert auf Archive und Container
# Nutzt: 7z, unzip, tar, p7zip

ROOT="$1"
LOGDIR="$HOME/.local/share/wallet-gui/logs"
LOGFILE="$LOGDIR/wallet_scan_archives.log"
STAGING="/tmp/wallet_scan_archives_$$"

mkdir -p "$LOGDIR"
mkdir -p "$STAGING"

echo "▶ Starte Archive-Scan auf: $ROOT" | tee -a "$LOGFILE"

# 1) Finde alle Archive
find "$ROOT" -type f \
  \( -iname '*.zip' -o -iname '*.rar' -o -iname '*.7z' \
     -o -iname '*.tar' -o -iname '*.tgz' -o -iname '*.tar.gz' \
     -o -iname '*.tar.xz' -o -iname '*.txz' \) | while read -r ARCH; do
    
    echo "→ Entpacke: $ARCH" | tee -a "$LOGFILE"
    
    # 2) Unterordner für jede Datei
    SUBDIR="$STAGING/$(basename "$ARCH")"
    mkdir -p "$SUBDIR"

    # 3) Versuche mit 7z, unzip, tar
    if 7z x -y -o"$SUBDIR" "$ARCH" &>/dev/null; then
        echo "   ✓ Mit 7z entpackt" | tee -a "$LOGFILE"
    elif unzip -q "$ARCH" -d "$SUBDIR" 2>/dev/null; then
        echo "   ✓ Mit unzip entpackt" | tee -a "$LOGFILE"
    elif tar -xf "$ARCH" -C "$SUBDIR" 2>/dev/null; then
        echo "   ✓ Mit tar entpackt" | tee -a "$LOGFILE"
    else
        echo "   ✗ Konnte $ARCH nicht entpacken" | tee -a "$LOGFILE"
        continue
    fi

    # 4) Wallet-Suche im entpackten Inhalt
    ~/.local/share/wallet-gui/scripts/wallet_harvest_any.sh "$SUBDIR" | tee -a "$LOGFILE"

done

echo "▶ Archive-Scan abgeschlossen. Logs: $LOGFILE"
rm -rf "$STAGING"
