#!/bin/bash
#
# Test: Terminal-Fenster Feature der Wallet GUI
# Testet ob Terminal-Modus funktioniert
#

echo "═══════════════════════════════════════════════════════════"
echo " 🧪 Terminal-Fenster Feature Test"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. Prüfe welche Terminals verfügbar sind
echo "1. Verfügbare Terminal-Emulatoren:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FOUND=0
for term in konsole gnome-terminal xfce4-terminal xterm x-terminal-emulator; do
    if command -v "$term" &>/dev/null; then
        echo "   ✓ $term gefunden: $(command -v $term)"
        FOUND=$((FOUND + 1))
    else
        echo "   ✗ $term nicht gefunden"
    fi
done
echo ""

if [ $FOUND -eq 0 ]; then
    echo "❌ FEHLER: Kein Terminal-Emulator gefunden!"
    echo ""
    echo "Bitte installiere einen:"
    echo "  • Fedora: sudo dnf install konsole"
    echo "  • Debian: sudo apt install gnome-terminal"
    echo "  • Arch: sudo pacman -S konsole"
    echo ""
    exit 1
fi

echo "✅ $FOUND Terminal-Emulator(en) verfügbar"
echo ""

# 2. Prüfe ob Test-Suite existiert
echo "2. Test-Suite Verfügbarkeit:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "/tmp/wallet_test_suite" ]; then
    FILES=$(find /tmp/wallet_test_suite -type f | wc -l)
    echo "   ✓ Test-Suite gefunden: /tmp/wallet_test_suite"
    echo "   ✓ Dateien: $FILES"
else
    echo "   ✗ Test-Suite nicht gefunden"
    echo ""
    echo "Erstelle Test-Suite..."
    if [ -f "scripts/create_test_wallets.sh" ]; then
        bash scripts/create_test_wallets.sh /tmp/wallet_test_suite
        echo "   ✓ Test-Suite erstellt"
    else
        echo "   ⚠ create_test_wallets.sh nicht gefunden"
        echo "   ℹ Test-Suite ist optional für Terminal-Test"
    fi
fi
echo ""

# 3. Prüfe Scanner
echo "3. Scanner Verfügbarkeit:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SCANNER="scripts/hrm_swarm_scanner_wrapper.sh"
if [ -f "$SCANNER" ]; then
    echo "   ✓ Scanner gefunden: $SCANNER"
    if [ -x "$SCANNER" ]; then
        echo "   ✓ Scanner ist ausführbar"
    else
        echo "   ⚠ Scanner nicht ausführbar, setze Rechte..."
        chmod +x "$SCANNER"
        echo "   ✓ Rechte gesetzt"
    fi
else
    echo "   ✗ Scanner nicht gefunden"
    echo ""
    echo "❌ Kann nicht testen ohne Scanner"
    exit 1
fi
echo ""

# 4. GUI-Test vorbereiten
echo "4. GUI Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "wallet_gui.py" ]; then
    echo "   ✓ wallet_gui.py gefunden"
    
    # Prüfe ob Terminal-Code vorhanden
    if grep -q "chkShowTerminal" wallet_gui.py; then
        echo "   ✓ Terminal-Checkbox implementiert"
    else
        echo "   ✗ Terminal-Checkbox nicht gefunden"
        echo "   ❌ Feature nicht implementiert!"
        exit 1
    fi
    
    if grep -q "open_scanner_terminal" wallet_gui.py; then
        echo "   ✓ open_scanner_terminal() Methode gefunden"
    else
        echo "   ✗ open_scanner_terminal() nicht gefunden"
        echo "   ❌ Feature nicht vollständig implementiert!"
        exit 1
    fi
else
    echo "   ✗ wallet_gui.py nicht gefunden"
    exit 1
fi
echo ""

# 5. Syntax-Check
echo "5. Python Syntax-Check:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 -m py_compile wallet_gui.py 2>&1; then
    echo "   ✓ Keine Syntax-Fehler gefunden"
else
    echo "   ❌ Syntax-Fehler gefunden!"
    exit 1
fi
echo ""

# 6. Test-Zusammenfassung
echo "═══════════════════════════════════════════════════════════"
echo " 📋 Test-Zusammenfassung"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ Terminal-Emulatoren: $FOUND verfügbar"
echo "✅ Scanner: Vorhanden und ausführbar"
echo "✅ GUI: Terminal-Feature implementiert"
echo "✅ Syntax: Keine Fehler"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo " 🚀 MANUELLER TEST"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Starte GUI:"
echo "   python3 wallet_gui.py"
echo ""
echo "2. In der GUI:"
echo "   • ROOT setzen (z.B. /tmp/wallet_test_suite)"
echo "   • Checkbox aktivieren: '🖥️ Terminal-Fenster beim Scan zeigen'"
echo "   • Scan-Button klicken"
echo ""
echo "3. Erwartetes Verhalten:"
echo "   • Externes Terminal-Fenster öffnet sich"
echo "   • Scanner-Output erscheint live im Terminal"
echo "   • Header mit Scanner-Info sichtbar"
echo "   • Nach Scan: Exit-Status angezeigt"
echo "   • Enter drücken → Terminal schließt"
echo "   • GUI lädt Ergebnisse automatisch"
echo ""
echo "4. Test verschiedener Szenarien:"
echo "   • Mit/ohne Terminal-Checkbox"
echo "   • Mit/ohne Root-Checkbox"
echo "   • Mit/ohne Auto-Mount"
echo "   • Verschiedene Targets (Ordner, Images)"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo " 💡 HINWEIS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Terminal-Feature Vorteile:"
echo "  • Transparenz - Sehen was Scanner tut"
echo "  • Debugging - Fehler sofort erkennbar"
echo "  • Fortschritt - Live-Status bei großen Scans"
echo "  • Vertrauen - Vollständige Sichtbarkeit"
echo ""
echo "Dokumentation:"
echo "  docs/TERMINAL_WINDOW_FEATURE.txt"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
