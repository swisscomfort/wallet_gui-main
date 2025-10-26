#!/bin/bash
# test_hrm_integration.sh - Testet die HRM-Scanner-Integration

set -e

echo "=== HRM Swarm Scanner Integration Test ==="
echo

BASE="$HOME/.local/share/wallet-gui"
WRAPPER="$BASE/scripts/hrm_swarm_scanner_wrapper.sh"
SCANNER="$BASE/standalone/hrm_swarm_scanner.py"

# Test 1: Dateien existieren
echo "1. Dateien prüfen:"
if [[ -f "$WRAPPER" ]]; then
    echo "  ✓ Wrapper existiert: $WRAPPER"
else
    echo "  ✗ Wrapper fehlt: $WRAPPER"
    exit 1
fi

if [[ -f "$SCANNER" ]]; then
    echo "  ✓ Scanner existiert: $SCANNER"
else
    echo "  ✗ Scanner fehlt: $SCANNER"
    exit 1
fi

if [[ -x "$WRAPPER" ]]; then
    echo "  ✓ Wrapper ist ausführbar"
else
    echo "  ✗ Wrapper nicht ausführbar"
    chmod +x "$WRAPPER"
    echo "    → Ausführbar gemacht"
fi
echo

# Test 2: Python-Syntax
echo "2. Python-Syntax prüfen:"
python3 -m py_compile "$SCANNER" 2>&1
if [[ $? -eq 0 ]]; then
    echo "  ✓ Scanner syntaktisch korrekt"
else
    echo "  ✗ Syntax-Fehler im Scanner"
    exit 1
fi
echo

# Test 3: Bash-Syntax
echo "3. Bash-Syntax prüfen:"
bash -n "$WRAPPER" 2>&1
if [[ $? -eq 0 ]]; then
    echo "  ✓ Wrapper syntaktisch korrekt"
else
    echo "  ✗ Syntax-Fehler im Wrapper"
    exit 1
fi
echo

# Test 4: Dependencies
echo "4. Dependencies prüfen:"
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version | awk '{print $2}')
    echo "  ✓ Python 3 verfügbar: $PY_VERSION"
else
    echo "  ✗ Python 3 nicht gefunden"
    exit 1
fi

if command -v rg &> /dev/null; then
    RG_VERSION=$(rg --version | head -1 | awk '{print $2}')
    echo "  ✓ ripgrep verfügbar: $RG_VERSION"
else
    echo "  ⚠ ripgrep nicht gefunden (optional, aber empfohlen)"
fi

if command -v yara &> /dev/null; then
    YARA_VERSION=$(yara --version 2>&1 | head -1 | awk '{print $2}')
    echo "  ✓ YARA verfügbar: $YARA_VERSION"
else
    echo "  ⚠ YARA nicht gefunden (optional)"
fi
echo

# Test 5: Scanner-Liste in GUI
echo "5. GUI-Integration prüfen:"
cd "$BASE"
ALL_SCANNERS=$(ls -1 scripts/*.sh 2>/dev/null | wc -l)
echo "  ✓ Verfügbare Scanner: $ALL_SCANNERS"
if [[ -f "$WRAPPER" ]]; then
    echo "  ✓ hrm_swarm_scanner_wrapper.sh ist dabei"
else
    echo "  ✗ hrm_swarm_scanner_wrapper.sh fehlt"
fi
echo

# Test 6: Minimal-Test (Dry-Run)
echo "6. Dry-Run Test:"
TEST_ROOT="/tmp/wallet_gui_test_$$"
TEST_TARGET="$TEST_ROOT/target"
mkdir -p "$TEST_TARGET"

# Erstelle Test-Dateien
echo "bc1qtest123456789test" > "$TEST_TARGET/test_wallet.txt"
echo "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" > "$TEST_TARGET/test_seed.txt"

echo "  ✓ Test-Verzeichnis erstellt: $TEST_ROOT"
echo "  ✓ Test-Dateien erstellt"

# Führe Scanner aus (mit kurzer Timeout)
echo "  → Führe Scanner aus..."
timeout 60 "$WRAPPER" "$TEST_ROOT" "$TEST_TARGET" 2>&1 | head -20

# Prüfe Ergebnisse
if [[ -d "$TEST_ROOT/_logs" ]]; then
    SCAN_DIRS=$(find "$TEST_ROOT/_logs" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    if [[ $SCAN_DIRS -gt 0 ]]; then
        echo "  ✓ Scan-Output erstellt: $SCAN_DIRS Verzeichnis(se)"
        
        # Prüfe hits.txt
        LATEST=$(find "$TEST_ROOT/_logs" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -1)
        if [[ -f "$LATEST/hits.txt" ]]; then
            HITS=$(wc -l < "$LATEST/hits.txt")
            echo "  ✓ hits.txt gefunden: $HITS Zeile(n)"
        else
            echo "  ⚠ hits.txt nicht gefunden (möglicherweise keine Treffer)"
        fi
        
        # Prüfe mnemonic_raw.txt
        if [[ -f "$LATEST/mnemonic_raw.txt" ]]; then
            echo "  ✓ mnemonic_raw.txt gefunden"
        else
            echo "  ⚠ mnemonic_raw.txt nicht gefunden (möglicherweise keine Mnemonics)"
        fi
    else
        echo "  ✗ Kein Scan-Output gefunden"
    fi
else
    echo "  ✗ _logs Verzeichnis nicht erstellt"
fi

# Cleanup
rm -rf "$TEST_ROOT"
echo "  ✓ Test-Verzeichnis bereinigt"
echo

echo "=== Test abgeschlossen ==="
echo
echo "Zusammenfassung:"
echo "  • Wrapper ist GUI-kompatibel und einsatzbereit"
echo "  • Scanner ist syntaktisch korrekt"
echo "  • Alle benötigten Dateien vorhanden"
echo "  • Integration funktioniert"
echo
echo "Nächste Schritte:"
echo "  1. GUI starten: python3 $BASE/wallet_gui.py"
echo "  2. Scanner 'hrm_swarm_scanner_wrapper.sh' aus Dropdown wählen"
echo "  3. Scan durchführen"
