#!/usr/bin/env bash
set -euo pipefail

SRC="$HOME/Downloads/wallet-gui"
INSTALL="$HOME/.local/share/wallet-gui"
mkdir -p "$INSTALL"

echo "==> 1) Abhängigkeiten"
sudo dnf install -y p7zip p7zip-plugins sleuthkit ntfs-3g || true
python3 -m pip install --user --upgrade pip >/dev/null
python3 -m pip install --user PyQt6 >/dev/null

echo "==> 2) GUI installieren/aktualisieren"
if [[ -x "$SRC/install_wallet_gui.sh" ]]; then
  (cd "$SRC" && ./install_wallet_gui.sh)
else
  cp -rf "$SRC"/* "$INSTALL"/
fi

echo "==> 3) Anleitung schreiben (MANUAL.html)"
cat > "$INSTALL/MANUAL.html" <<'HTML'
<!doctype html><meta charset="utf-8">
<style>
body{font:14px/1.45 system-ui,Segoe UI,Roboto,Ubuntu,sans-serif;margin:0;padding:14px;color:#ddd;background:#222}
h1{font-size:22px;margin:.3em 0} h2{font-size:18px;margin:.8em 0 .3em}
.box{background:#2a2a2a;border:1px solid #3a3a3a;border-radius:8px;padding:10px;margin:8px 0}
code{background:#333;padding:.1em .3em;border-radius:4px}
</style>
<h1>Wallet GUI – Kurz-Anleitung</h1>
<div class="box"><b>ROOT</b>: Arbeitsordner (Logs/Mounts/Staging). <b>Scanner</b>: Script (wallet_harvest_any.sh).</div>
<h2>Ziele</h2>
<div class="box">Ordner / Datei-Abbild / Gerät hinzufügen · Auswahl entfernen · Liste leeren.</div>
<h2>Optionen</h2>
<div class="box"><b>Aggressiv</b> = tiefere Suche; <b>Staging anlegen</b> = Symlinks unter ROOT/Software/_staging_wallets/;
<b>Mit Root</b> + <b>Auto-Mount</b> (ro) für Images/Devices unter ROOT/_mount/&lt;name&gt;/.</div>
<h2>Aktionen</h2>
<div class="box">Scan starten · ROOT in Dolphin · Staging öffnen · Logs öffnen.</div>
<h2>Ergebnisse</h2>
<div class="box"><b>Live-Log</b> (Ablauf) • <b>Hits</b> (wallet.dat, electrum, metamask, bip39/bip32, mnemonic/seed, xpub/xprv, bc1…, 0x…)
• <b>Mnemonics</b> (grobe 12/24-Wort Kandidaten) • <b>Anleitung</b> (diese Seite).</div>
<h2>Typischer Ablauf</h2>
<ol><li>ROOT wählen</li><li>Ziele hinzufügen</li><li>Bei Images/Devices: „Mit Root“ + „Auto-Mount“</li><li>Scan starten → Tabs prüfen</li></ol>
<h2>Schreibt Pfade</h2>
<ul><li>ROOT/_logs/walletscan_YYYYMMDD_HHMMSS/</li><li>ROOT/_mount/&lt;name&gt;/</li><li>ROOT/Software/_staging_wallets/</li></ul>
HTML

echo "==> 4) GUI patchen (QtGui-Fix + Tab „Anleitung“)"
python3 - "$INSTALL/wallet_gui.py" "$SRC/wallet_gui.py" <<'PY'
import sys, re
from pathlib import Path

def patch(p: Path):
    if not p.exists(): 
        print(f"[SKIP] {p} fehlt"); return
    s = p.read_text(encoding="utf-8")
    # QtGui import & moveCursor-Fix
    s = re.sub(r"from PyQt6 import QtWidgets, QtCore(?!, QtGui)",
               "from PyQt6 import QtWidgets, QtCore, QtGui", s)
    s = s.replace("self.logView.moveCursor(self.logView.textCursor().End)",
                  "self.logView.moveCursor(QtGui.QTextCursor.MoveOperation.End)")
    # Anleitung-Tab einfügen (nach „Mnemonics“-Tab)
    if "self.helpView" not in s:
        inj = (
            '        # Hilfe/Anleitung-Tab\n'
            '        self.helpView = QtWidgets.QTextBrowser()\n'
            '        self.helpView.setOpenExternalLinks(True)\n'
            '        try:\n'
            '            from pathlib import Path\n'
            '            _p_local = Path(__file__).with_name("MANUAL.html")\n'
            '            _p_inst  = Path.home()/".local"/"share"/"wallet-gui"/"MANUAL.html"\n'
            '            if _p_local.exists():\n'
            '                self.helpView.setHtml(_p_local.read_text(encoding="utf-8"))\n'
            '            elif _p_inst.exists():\n'
            '                self.helpView.setHtml(_p_inst.read_text(encoding="utf-8"))\n'
            '            else:\n'
            '                self.helpView.setHtml("<h3>Wallet GUI – Anleitung</h3><p>MANUAL.html nicht gefunden.</p>")\n'
            '        except Exception as e:\n'
            '            self.helpView.setPlainText(f"Fehler beim Laden der Anleitung: {e}")\n'
            '        self.tabs.addTab(self.helpView, "Anleitung")\n'
        )
        s = re.sub(r'(self\.tabs\.addTab\([^\n]*"Mnemonics"[^\n]*\)\s*\n)', r"\1"+inj, s, count=1, flags=re.M)
    p.write_text(s, encoding="utf-8")
    print(f"[OK] gepatcht: {p}")

for a in sys.argv[1:]:
    patch(Path(a))
PY

echo -e "\n==> Fertig. Start:\n   wallet-gui  ||  python3 \"$INSTALL/wallet_gui.py\""
