#!/bin/bash
# Test-Skript für GUI-Scanner-Organisation

echo "=== Wallet GUI Scanner Test ==="
echo

BASE="$HOME/.local/share/wallet-gui"

echo "1. Verzeichnisstruktur:"
ls -la "$BASE" | grep -E "^d"
echo

echo "2. GUI-Scanner (scripts/):"
ls -1 "$BASE/scripts/"*.{sh,py} 2>/dev/null | while read f; do
    echo "  ✓ $(basename "$f")"
done
echo

echo "3. Standalone-Scanner (standalone/):"
ls -1 "$BASE/standalone/"*.{sh,py} 2>/dev/null | while read f; do
    echo "  ✓ $(basename "$f")"
done
echo

echo "4. GUI-Test (Syntax-Check):"
cd "$BASE"
python3 -m py_compile wallet_gui.py 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ wallet_gui.py syntaktisch korrekt"
else
    echo "  ✗ Fehler in wallet_gui.py"
fi
echo

echo "5. Standalone-Scanner Test:"
cd "$BASE"
python3 -m py_compile standalone/hrm_swarm_scanner.py 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ hrm_swarm_scanner.py syntaktisch korrekt"
else
    echo "  ✗ Fehler in hrm_swarm_scanner.py"
fi
echo

echo "=== Test abgeschlossen ==="
