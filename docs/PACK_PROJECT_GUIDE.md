# Project Bundle Creator 📦

## 🎯 Übersicht

Das `pack_project.sh` Script erstellt selbstentpackende `.run` Bundles für einfache Projekt-Distribution und Deployment.

## ⚡ Features

- 📦 **Self-extracting bundles** - Einzelne `.run` Datei enthält komplettes Projekt
- 🔐 **SHA256 Integrität** - Automatische Verifikation beim Entpacken
- 🤖 **Auto-Detection** - Erkennt und startet automatisch:
  - 🐳 Docker Projekte (Dockerfile)
  - 🐍 Python Projekte (main.py/app.py)
  - 📦 Node.js Projekte (package.json)
  - 🔧 Shell Scripts (run.sh)
- 🧹 **Smart Excludes** - Ignoriert `.git`, `__pycache__`, `node_modules`, etc.
- 📊 **Detailliertes Logging** - Vollständige Ausgabe des Pack/Unpack Prozesses

## 🚀 Installation & Verwendung

### Direkter Download:
```bash
# Download des Scripts
curl -O https://raw.githubusercontent.com/swisscomfort/wallet_gui-main/main/tools/pack_project.sh
chmod +x pack_project.sh
```

### Verwendung:
```bash
# Aktuelles Verzeichnis packen
./pack_project.sh .

# Spezifisches Projekt packen
./pack_project.sh /pfad/zum/projekt

# Mit custom Output-Namen
./pack_project.sh . mein-project-bundle.run
```

### Bundle ausführen:
```bash
chmod +x project-bundle.run
./project-bundle.run
```

## 📋 Systemvoraussetzungen

- `bash` (≥4.0)
- `tar`, `gzip`
- `sha256sum`
- `python3` (für Python-Projekte)
- `docker` (für Docker-Projekte)
- `npm` (für Node.js-Projekte)

## 🔍 Was wird ausgeschlossen?

- `.git/` - Git Repository Daten
- `.venv/`, `venv/` - Python Virtual Environments  
- `__pycache__/`, `*.pyc` - Python Cache
- `build/`, `dist/` - Build Artefakte
- `node_modules/` - Node.js Dependencies
- `.DS_Store` - macOS System Dateien
- `*.egg-info/` - Python Package Info

## 📊 Beispiel Output

```
[OK] Project directory: .
[OK] All required tools available  
[INFO] Workspace: /tmp/tmp.ABC123
[INFO] Packaging project files...
[OK] Project packaged
[INFO] Creating payload...
[OK] Payload ready: 1295245 bytes, SHA256: 595e0d942dd0...
[INFO] Creating self-extracting bundle...
[OK] Bundle created: myproject-bundle-20251026-164918.run
[OK] Size: 1295245 bytes
[OK] SHA256: 595e0d942dd0c7161d7f28f05f7c53502e06d66445e106ba5ac7428f2034013b

=== Summary ===
Output:   myproject-bundle-20251026-164918.run
Project:  .
Usage:    chmod +x myproject-bundle-20251026-164918.run && ./myproject-bundle-20251026-164918.run
```

## 🛡️ Sicherheit

- SHA256 Integritätsprüfung verhindert manipulierte Bundles
- Temporary Dateien werden automatisch bereinigt
- Keine privilegierten Rechte erforderlich

## 📝 Lizenz

MIT License - Siehe [LICENSE](../LICENSE) für Details.

---

**Entwickelt für einfache Projekt-Distribution und Deployment 🚀**