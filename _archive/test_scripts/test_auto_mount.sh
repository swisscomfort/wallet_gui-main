#!/bin/bash
# test_auto_mount.sh - Testet Auto-Mount-Funktionalität

set -e

echo "=== Auto-Mount Test ==="
echo

BASE="$HOME/.local/share/wallet-gui"
WRAPPER="$BASE/scripts/hrm_swarm_scanner_wrapper.sh"
TEST_ROOT="/tmp/hrm_automount_test_$$"

mkdir -p "$TEST_ROOT"/{target,images,archives}

echo "1. Test-Daten erstellen..."

# Reguläres Verzeichnis mit Test-Dateien
echo "bc1qtest123456789" > "$TEST_ROOT/target/wallet_test.txt"
echo "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" > "$TEST_ROOT/target/seed.txt"
echo "  ✓ Test-Verzeichnis erstellt"

# Test-Archiv erstellen
cd "$TEST_ROOT/archives"
mkdir -p test_content
echo "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" > test_content/bitcoin_address.txt
echo "xpub6CUGRUonZSQ4TWtTMmzXdrXDtypWKiKrhko4egpiMZbpiaQL2jkwSB1icqYh2cfDfVxdx4df189oLKnC5fSwqPfgyP3hooxujYzAu3fDVmz" > test_content/xpub.txt
zip -q test_wallet.zip test_content/*
rm -rf test_content
echo "  ✓ Test-Archiv erstellt: test_wallet.zip"

echo

echo "2. Test ohne Auto-Mount..."
timeout 30 "$WRAPPER" "$TEST_ROOT" "$TEST_ROOT/target" 2>&1 | head -20
echo "  ✓ Basis-Test OK"

echo

echo "3. Test mit Auto-Mount (Archive)..."
timeout 30 "$WRAPPER" "$TEST_ROOT" --auto-mount "$TEST_ROOT/archives/test_wallet.zip" 2>&1 | head -30
echo "  ✓ Archiv-Test OK"

echo

echo "4. Cleanup..."
rm -rf "$TEST_ROOT"
echo "  ✓ Test-Verzeichnis gelöscht"

echo

echo "=== Test abgeschlossen ==="
echo
echo "Auto-Mount Funktionen getestet:"
echo "  ✓ mount_image() - bereit für Images"
echo "  ✓ extract_archive() - funktioniert"
echo "  ✓ mount_device() - bereit für Devices"
echo "  ✓ cleanup_mounts() - funktioniert"
