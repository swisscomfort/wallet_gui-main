#!/bin/bash
# wallet_scan_images.sh
# Automatisches Mounten & Scannen von Disk-Images nach Wallet-Artefakten

ROOT="$1"
LOGDIR="$HOME/.local/share/wallet-gui/logs"
LOGFILE="$LOGDIR/wallet_scan_images.log"
MOUNTBASE="/tmp/wallet_scan_mounts_$$"

mkdir -p "$LOGDIR"
mkdir -p "$MOUNTBASE"

echo "▶ Starte Image-Scan auf: $ROOT" | tee -a "$LOGFILE"

find "$ROOT" -type f \
  \( -iname '*.iso' -o -iname '*.img' -o -iname '*.dmg' \
     -o -iname '*.vhd' -o -iname '*.vhdx' -o -iname '*.qcow2' \) | while read -r IMG; do
    
    echo "→ Versuche zu mounten: $IMG" | tee -a "$LOGFILE"

    SUBMOUNT="$MOUNTBASE/$(basename "$IMG")"
    mkdir -p "$SUBMOUNT"

    # Mount versuchen (loop, read-only)
    if sudo mount -o loop,ro "$IMG" "$SUBMOUNT" 2>/dev/null; then
        echo "   ✓ Gemountet unter $SUBMOUNT" | tee -a "$LOGFILE"
    else
        echo "   ✗ Konnte $IMG nicht mounten" | tee -a "$LOGFILE"
        rmdir "$SUBMOUNT"
        continue
    fi

    # Wallet-Suche im gemounteten Image
    ~/.local/share/wallet-gui/scripts/wallet_harvest_any.sh "$SUBMOUNT" | tee -a "$LOGFILE"

    # wieder aushängen
    sudo umount "$SUBMOUNT"
    rmdir "$SUBMOUNT"
done

echo "▶ Image-Scan abgeschlossen. Logs: $LOGFILE"
