# Standalone Scanner

Dieser Ordner enthält **unabhängige Scanner**, die **NICHT** über die GUI laufen,
sondern direkt von der Kommandozeile ausgeführt werden.

## ⚠️ WICHTIG: Root-Rechte für Images/Devices

**Images (.img, .iso, .dd) und Devices (/dev/sdX) scannen:**
- Benötigt **Root-Rechte** (losetup/mount)
- In GUI: ☑ "Mit Root (pkexec) für Auto-Mount" aktivieren!
- CLI: `sudo` oder `pkexec` voranstellen

**Normale Verzeichnisse scannen:**
- Keine Root-Rechte nötig
- Funktioniert als normaler Benutzer

## Zweck

Standalone-Scanner sind:
- Vollständig eigenständige Programme
- Haben eigene Parameter und Ausgabeformate
- Benötigen KEINE GUI-Integration
- Können manuell oder in Skripten verwendet werden

## Enthaltene Scanner

### hrm_swarm_scanner.py

Ein HRM-style Swarm Scanner für paralleles Wallet-Scanning.

**Verwendung:**
```bash
python3 /home/emil/.local/share/wallet-gui/standalone/hrm_swarm_scanner.py \
  --root /mnt/mediacenter1/sido \
  --target /mnt/mediacenter1/sido \
  --threads 8 \
  --max-mb 512 \
  --prefer-rg \
  --yara
```

**Parameter:**
- `--root`: Arbeitsverzeichnis (Logs werden hier unter `_logs/` gespeichert)
- `--target`: Scan-Ziel (mehrfach möglich)
- `--threads`: Anzahl paralleler Threads (Standard: 6)
- `--max-mb`: Maximale Dateigröße in MB (Standard: 256)
- `--exclude`: Regex für auszuschließende Pfade
- `--prefer-rg`: Verwendet ripgrep wenn verfügbar
- `--yara`: Aktiviert YARA-Scans
- `--rules`: Pfad zu YARA-Regeln (.yar)

**Ausgabe:**
```
<root>/_logs/hrm_swarm_<timestamp>/
  ├── hits.json          # Wallet-Treffer mit Scoring
  ├── yara.json          # YARA-Scan Ergebnisse
  ├── mnemonics.json     # Gefundene Seed-Phrases
  └── summary.json       # Statistik-Zusammenfassung
```

## GUI vs. Standalone

| Merkmal | GUI-Scanner (scripts/) | Standalone |
|---------|------------------------|------------|
| Ausführung | Über wallet_gui.py | Direkt CLI |
| Ausgabe | _logs/walletscan_* | Eigenes Format |
| Parameter | --aggressive, --staging | Scanner-spezifisch |
| Integration | Ja | Nein |
| Verwendung | Interaktiv | Automatisierung |

## Hinweise

- Standalone-Scanner können **nicht** über die GUI gestartet werden
- Für GUI-Integration: Scanner nach `scripts/` verschieben und anpassen
- Diese Scanner sind für fortgeschrittene Nutzer und Automatisierung
