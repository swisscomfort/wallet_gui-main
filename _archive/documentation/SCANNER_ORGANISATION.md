# Wallet GUI - Scanner Organisation

## Verzeichnisstruktur

```
wallet-gui/
├── wallet_gui.py           # Haupt-GUI-Anwendung
├── scripts/                # GUI-kompatible Scanner
│   ├── wallet_harvest_any.sh
│   ├── wallet_harvest_any_gui.sh
│   ├── wallet_scan_images.sh
│   └── wallet_scan_archives.sh
├── standalone/             # Standalone-Scanner (NICHT GUI-kompatibel)
│   ├── hrm_swarm_scanner.py
│   └── README.md
├── hrm_swarm/             # HRM Swarm Framework (GUI-integriert)
│   ├── agents/
│   └── ...
└── tools/                 # Hilfs-Tools
```

## Scanner-Typen

### 1. GUI-Scanner (scripts/)

**Eigenschaften:**
- ✅ Über wallet_gui.py bedienbar
- ✅ Standard-Parameter: `<script> <root> [--aggressive] [--staging] [--auto-mount] <targets...>`
- ✅ Ausgabe: `_logs/walletscan_<timestamp>/`
- ✅ Live-Log-Ausgabe in GUI
- ✅ Automatisches Laden der Ergebnisse

**Verfügbare Scanner:**
- `wallet_harvest_any.sh` - Standard-Scanner (empfohlen)
- `wallet_harvest_any_gui.sh` - GUI-optimierte Version
- `wallet_scan_images.sh` - Image/ISO Scanner
- `wallet_scan_archives.sh` - Archiv-Scanner (ZIP, TAR, etc.)

**Verwendung in GUI:**
1. Scanner aus Dropdown-Liste wählen
2. ROOT und Targets setzen
3. Optionen aktivieren (Aggressiv, Staging, etc.)
4. "Scan starten" klicken

### 2. Standalone-Scanner (standalone/)

**Eigenschaften:**
- ❌ NICHT über GUI bedienbar
- ✅ Eigene Parameter und Ausgabeformate
- ✅ Für CLI und Automatisierung
- ✅ Fortgeschrittene Features

**Verfügbare Scanner:**
- `hrm_swarm_scanner.py` - HRM-style Parallel-Scanner mit YARA

**Verwendung per CLI:**
```bash
cd ~/.local/share/wallet-gui
python3 standalone/hrm_swarm_scanner.py \
  --root /run/media/emil/DATEN \
  --target /run/media/emil/DATEN \
  --threads 8 \
  --prefer-rg \
  --yara
```

### 3. HRM Swarm Framework (hrm_swarm/)

**Eigenschaften:**
- ✅ Modulares Agent-System
- ✅ Kann in GUI integriert werden
- ✅ Policy-basierte Eskalation
- ✅ Python-Module

**Verwendung:**
```bash
python3 -m hrm_swarm --root /path --target /path
```

## GUI-Funktionen

### Scanner-Auswahl

Die GUI bietet jetzt:
- **Dropdown-Menü** mit allen verfügbaren Scannern aus `scripts/`
- **"Eigener Scanner…"** Button für custom Scanner
- **Warnung** bei Auswahl von Standalone-Scannern
- **⭐ Markierung** für manuell hinzugefügte Scanner

### Scanner hinzufügen

**Als GUI-Scanner (empfohlen):**
1. Skript nach `scripts/` kopieren
2. Sicherstellen, dass es die Standard-Parameter unterstützt:
   ```bash
   script.sh <ROOT> [--aggressive] [--staging] [--auto-mount] <target1> <target2>...
   ```
3. Ausgabe nach `<ROOT>/_logs/walletscan_<timestamp>/` schreiben
4. GUI neu starten → Scanner erscheint automatisch im Dropdown

**Als Standalone-Scanner:**
1. Skript nach `standalone/` kopieren
2. Eigene Parameter und Ausgabe-Format verwenden
3. README in `standalone/` dokumentieren
4. Per CLI ausführen

## Best Practices

### Scanner-Entwicklung

**Für GUI-Integration:**
```bash
#!/bin/bash
ROOT="$1"
shift
# Parse optionale Flags
AGGRESSIVE=0
STAGING=0
AUTO_MOUNT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --aggressive) AGGRESSIVE=1; shift ;;
    --staging) STAGING=1; shift ;;
    --auto-mount) AUTO_MOUNT=1; shift ;;
    *) break ;;
  esac
done
TARGETS=("$@")

# Ausgabe-Verzeichnis
OUT="$ROOT/_logs/walletscan_$(date +%s)"
mkdir -p "$OUT"

# Ausgabe für GUI
echo "OUT=$OUT"

# Scanner-Logik...
```

**Für Standalone:**
- Keine Einschränkungen
- Eigenes Argument-Parsing (argparse, getopts, etc.)
- Eigenes Ausgabe-Format
- Dokumentation in `standalone/README.md`

## Migration

### Existierende Scanner GUI-kompatibel machen:

1. **Standardparameter implementieren**
2. **Ausgabe nach `_logs/walletscan_*/` schreiben**
3. **`OUT=<pfad>` ausgeben für Auto-Load**
4. Nach `scripts/` verschieben

### Scanner als Standalone auslagern:

1. Nach `standalone/` verschieben
2. Eigene Parameter/Ausgabe verwenden
3. In `standalone/README.md` dokumentieren
4. CLI-Dokumentation in Kommentaren

## Wartung

### GUI aktualisieren:
```bash
cd ~/.local/share/wallet-gui
git pull  # falls Git-Repo
# oder
./install_wallet_gui.sh
```

### Scanner hinzufügen/entfernen:
- **GUI-Scanner:** einfach in `scripts/` ablegen/löschen
- **Standalone:** in `standalone/` verwalten

### Logs bereinigen:
```bash
# Alte Logs löschen (älter als 30 Tage)
find ~/.local/share/wallet-gui/_logs -type d -mtime +30 -exec rm -rf {} +
```

## Fehlerbehebung

### Scanner erscheint nicht in GUI:
1. Prüfen ob in `scripts/` (nicht `standalone/`)
2. Dateirechte prüfen: `chmod +x scripts/scanner.sh`
3. GUI neu starten

### Scanner startet nicht:
1. Log-Ausgabe in "Live-Log" Tab prüfen
2. Scanner manuell per CLI testen
3. Parameter prüfen (ROOT, Targets)

### Standalone-Scanner in GUI nicht wählbar:
- **Das ist Absicht!** Standalone-Scanner sind nicht GUI-kompatibel
- Per CLI ausführen oder nach `scripts/` migrieren

## Weitere Informationen

- **GUI-Dokumentation:** MANUAL.html oder MANUAL_INTERACTIVE.html
- **Standalone-Scanner:** standalone/README.md
- **HRM-Framework:** hrm_swarm/README.md
