# FSearch & KDialog Integration 🔍

**Datum:** 7. Oktober 2025  
**Status:** ✅ KOMPLETT INTEGRIERT

## 🎯 Problem gelöst

Qt-Dialoge zeigten keine Dateien in Dolphin-sichtbaren Ordnern.  
→ **Lösung:** Native Linux-Tools nutzen!

## ✨ Neue Integration

### Primär: KDialog (KDE)
- **Was:** Native KDE-Dialoge
- **Warum:** 
  - ✅ Perfekt in KDE/Plasma integriert
  - ✅ Zeigt ALLE Dateien (keine Filter-Probleme)
  - ✅ Mehrfachauswahl funktioniert einwandfrei
  - ✅ Nutzt Dolphin-Backend
- **Features:**
  - Multi-Selektion mit `--multiple --separate-output`
  - Filter für Images/Archive
  - Startet in benutzerdefinierten Pfaden

### Sekundär: FSearch
- **Was:** Schneller Datei-Sucher
- **Wann:** Zusätzlich verfügbar für manuelle Suche
- **Warum:** 
  - ✅ Blitzschnelle Echtzeitsuche
  - ✅ Regex-Support
  - ✅ Kann große Dateisysteme durchsuchen

### Fallback: Qt-Dialog
- **Wann:** Wenn weder kdialog noch FSearch verfügbar
- **Status:** Bleibt als Fallback erhalten

## 🔧 Implementierung

### 1. ROOT-Auswahl
```python
# Nutzt kdialog wenn verfügbar
kdialog --title "ROOT-Verzeichnis auswählen" \
        --getexistingdirectory /run/media

# Fallback: Qt-Dialog (1200x800)
```

### 2. Ordner hinzufügen
```python
# Multi-Selektion mit kdialog
kdialog --title "Ordner hinzufügen" \
        --multiple --separate-output \
        --getexistingdirectory /run/media

# Output: Mehrere Pfade (einer pro Zeile)
# /run/media/emil/USB1
# /run/media/emil/USB2
# /mnt/backup
```

### 3. Dateien hinzufügen
```python
# Multi-Selektion mit Filter
kdialog --title "Datei/Abbild hinzufügen" \
        --multiple --separate-output \
        --getopenfilename /run/media \
        "*.img *.iso|Disk-Images
         *.zip *.7z|Archive
         *|Alle Dateien"

# Zeigt automatisch Dateigrößen im Log:
# ✓ Datei hinzugefügt: backup.img (250.5 MB)
```

### 4. Devices hinzufügen
```python
# Startet in /dev/disk/by-label für lesbare Namen
kdialog --title "Device wählen" \
        --multiple --separate-output \
        --getopenfilename /dev/disk/by-label

# Warnt automatisch wenn Root-Rechte fehlen
```

## 📊 Vorher/Nachher

| Feature | Qt-Dialog ❌ | KDialog ✅ |
|---------|-------------|-----------|
| Zeigt .img Dateien | Manchmal nicht | **Immer** |
| Multi-Selektion | Buggy | **Perfekt** |
| KDE-Integration | Fremd | **Native** |
| Dolphin-Backend | Nein | **Ja** |
| Filter-Support | Kompliziert | **Einfach** |
| Performance | Okay | **Schnell** |

## 🎨 User Experience

### Workflow: Mehrere Images scannen

**Alt (Qt-Dialog):**
```
1. Button klicken
2. Dialog öffnet (zeigt evtl. keine .img Dateien!)
3. Filter manuell umschalten auf "Alle Dateien"
4. Datei auswählen
5. Dialog schließen
6. Wiederholen für jede Datei... 😫
```

**Neu (KDialog):**
```
1. Button klicken
2. KDialog öffnet (zeigt ALLES wie Dolphin!)
3. Strg+Klick auf mehrere .img Dateien
4. "Öffnen" → Alle hinzugefügt mit Größenangabe! 🚀
```

## 🔍 FSearch-Nutzung

FSearch wird **zusätzlich** geöffnet wenn verfügbar:

```python
# run_fsearch_dialog() öffnet FSearch parallel
subprocess.Popen(["fsearch", "--path", initial_path])

# User kann dann in FSearch suchen und Pfade kopieren
```

**Vorteil:** 
- Schnelle Suche über große Dateisysteme
- Regex-Support: `.*backup.*\.img$`
- Echtzeitsuche während Dialog offen

## 🧪 Test-Szenarien

### Test 1: Image in /mnt/mediacenter1/sido/
```bash
# Vorher: Qt-Dialog zeigt NICHTS (leer)
# Nachher: KDialog zeigt volume_disk_2025-10-06-1346.img (232.9 GiB)
✅ FUNKTIONIERT!
```

### Test 2: Mehrere USB-Sticks
```bash
# KDialog mit Multi-Selektion
Pfad: /dev/disk/by-label/
Auswahl: USB_BACKUP, OLD_HDD, FORENSICS_DRIVE
→ Alle 3 zur Liste hinzugefügt
✅ FUNKTIONIERT!
```

### Test 3: Große Archive-Sammlung
```bash
# Strg+Klick auf 15 .zip Dateien
→ Alle 15 mit Größenangabe hinzugefügt
✅ FUNKTIONIERT!
```

## 📦 Dependencies

### Erforderlich:
- **kdialog** (Teil von KDE Plasma)
  ```bash
  sudo pacman -S kdialog  # Arch
  sudo apt install kdialog  # Debian/Ubuntu
  ```

### Optional:
- **fsearch** (für Zusatz-Features)
  ```bash
  sudo pacman -S fsearch  # Arch
  # Oder von: https://github.com/cboxdoerfer/fsearch
  ```

## 🔧 Technische Details

### KDialog Parameter
```bash
# Verzeichnis wählen
--getexistingdirectory <initial_path>

# Datei wählen
--getopenfilename <initial_path> [filter]

# Multi-Selektion
--multiple --separate-output

# Filter-Format
"*.ext1 *.ext2|Label1
 *.ext3|Label2
 *|Alle Dateien"
```

### Filter-Beispiele
```python
# Images
"*.img *.IMG *.iso *.ISO *.dd *.DD|Disk-Images"

# Archive
"*.zip *.ZIP *.rar *.RAR *.7z *.7Z|Archive"

# Alle
"*|Alle Dateien"
```

### Output-Parsing
```python
result = subprocess.run(
    ["kdialog", "--multiple", "--separate-output", ...],
    capture_output=True, text=True
)

# Output format (one path per line):
# /path/to/file1.img
# /path/to/file2.img
# /path/to/file3.img

for path in result.stdout.strip().split('\n'):
    if path:
        process_path(path)
```

## ✅ Status Check

```bash
# Prüfe Installation
which kdialog    # /usr/bin/kdialog
which fsearch    # /usr/bin/fsearch (optional)

# Test kdialog
kdialog --getopenfilename /home

# Test fsearch
fsearch --path /home
```

## 🎯 Vorteile der Integration

1. **Native KDE-Integration**
   - Sieht aus wie Dolphin
   - Nutzt gleiche Backends
   - Konsistentes Look & Feel

2. **Keine Filter-Probleme mehr**
   - Zeigt ALLE Dateien wie Dolphin
   - Keine versteckten .img Dateien
   - Keine case-sensitivity-Issues

3. **Bessere Performance**
   - Native C/C++ Implementierung
   - Schneller als Qt-Python-Dialoge
   - Weniger Ressourcen

4. **Bewährte Tools**
   - KDialog seit Jahren stabil
   - Von KDE-Community maintained
   - Millionen User nutzen es täglich

5. **Fallback vorhanden**
   - Qt-Dialog bleibt als Backup
   - Funktioniert auch ohne kdialog
   - Keine Abhängigkeit

## 🚀 Resultat

**Vorher:** "Das Image wird nicht angezeigt!" 😡  
**Nachher:** Native KDE-Dialoge, alles sichtbar! 🎉

**Problem gelöst:** ✅  
**Integration:** ✅  
**Testing:** ✅  
**Dokumentation:** ✅  

---

**Von Qt-Chaos zu KDE-Native-Excellence! 🏆**
