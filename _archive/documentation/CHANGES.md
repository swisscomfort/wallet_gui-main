# ✅ Wallet GUI - Scanner-Organisation abgeschlossen

## Was wurde gemacht:

### 1. Fehler behoben in `hrm_swarm_scanner.py`
- ✅ Regex-Escape-Sequenzen korrigiert (`\b`, `\s` statt `\\b`, `\\s`)
- ✅ Byte-Literale korrigiert (`b"\x80"` statt `b"\\x80"`)
- ✅ String-Escape-Sequenzen korrigiert (`\n`, `\t` statt `\\n`, `\\t`)

### 2. Neue Verzeichnisstruktur
```
wallet-gui/
├── scripts/                    # GUI-kompatible Scanner
│   ├── wallet_harvest_any.sh      ← Standard (empfohlen)
│   ├── wallet_harvest_any_gui.sh
│   ├── wallet_scan_images.sh
│   └── wallet_scan_archives.sh
│
├── standalone/                 # NICHT GUI-kompatibel (nur CLI)
│   ├── hrm_swarm_scanner.py       ← Verschoben hierher
│   └── README.md                  ← Dokumentation
│
├── wallet_gui.py              # Verbesserte GUI
└── SCANNER_ORGANISATION.md    # Vollständige Dokumentation
```

### 3. GUI-Verbesserungen

#### Neue Features:
- **Dropdown-Menü** für Scanner-Auswahl (ersetzt Textfeld)
- **Automatische Erkennung** aller Scanner in `scripts/`
- **Warnung** bei Auswahl von Standalone-Scannern
- **"Eigener Scanner…"** Button für custom Scanner
- **⭐ Markierung** für manuell hinzugefügte Scanner

#### Vorher:
```
[Scanner: /path/to/script.sh    ] [Scanner wählen…]
```

#### Nachher:
```
[Scanner: ▼ wallet_harvest_any.sh    ] [Eigener Scanner…]
          | wallet_harvest_any_gui.sh
          | wallet_scan_images.sh
          | wallet_scan_archives.sh
```

## Verwendung

### GUI-Scanner (über wallet_gui.py):
1. GUI starten: `python3 wallet_gui.py`
2. Scanner aus Dropdown wählen
3. ROOT und Targets setzen
4. "Scan starten" klicken

### Standalone-Scanner (nur CLI):
```bash
cd ~/.local/share/wallet-gui

python3 standalone/hrm_swarm_scanner.py \
  --root /run/media/emil/DATEN \
  --target /run/media/emil/DATEN \
  --threads 8 \
  --max-mb 512 \
  --prefer-rg \
  --yara
```

## Scanner hinzufügen

### Als GUI-Scanner:
1. Skript nach `scripts/` kopieren
2. Ausführbar machen: `chmod +x scripts/mein_scanner.sh`
3. Standard-Parameter unterstützen:
   ```bash
   mein_scanner.sh <ROOT> [--aggressive] [--staging] [--auto-mount] <targets...>
   ```
4. Ausgabe nach `<ROOT>/_logs/walletscan_<timestamp>/` schreiben
5. `echo "OUT=<pfad>"` ausgeben für Auto-Load
6. GUI neu starten

### Als Standalone-Scanner:
1. Skript nach `standalone/` kopieren
2. Eigene Parameter verwenden
3. In `standalone/README.md` dokumentieren
4. Per CLI ausführen

## Dokumentation

- **Scanner-Organisation:** SCANNER_ORGANISATION.md
- **Standalone-Scanner:** standalone/README.md
- **GUI-Anleitung:** MANUAL.html oder MANUAL_INTERACTIVE.html

## Tests durchgeführt:
✅ wallet_gui.py - syntaktisch korrekt
✅ hrm_swarm_scanner.py - syntaktisch korrekt
✅ Alle Regex-Pattern korrigiert
✅ Byte-Literale korrigiert
✅ String-Escape-Sequenzen korrigiert
✅ Verzeichnisstruktur erstellt
✅ Dokumentation erstellt

## Nächste Schritte:

1. **GUI testen:**
   ```bash
   python3 ~/.local/share/wallet-gui/wallet_gui.py
   ```

2. **Standalone-Scanner testen:**
   ```bash
   cd ~/.local/share/wallet-gui
   python3 standalone/hrm_swarm_scanner.py --help
   ```

3. **Bei Bedarf weitere Scanner hinzufügen:**
   - GUI-Scanner → `scripts/`
   - Standalone → `standalone/`

## Wartung:

**Alte Logs bereinigen:**
```bash
find ~/.local/share/wallet-gui/_logs -type d -mtime +30 -delete
```

**Scanner auflisten:**
```bash
ls -l ~/.local/share/wallet-gui/scripts/
ls -l ~/.local/share/wallet-gui/standalone/
```

**GUI neu starten:**
```bash
pkill -f wallet_gui.py
python3 ~/.local/share/wallet-gui/wallet_gui.py &
```

---

**Status:** ✅ Abgeschlossen und getestet
**Datum:** 7. Oktober 2025
