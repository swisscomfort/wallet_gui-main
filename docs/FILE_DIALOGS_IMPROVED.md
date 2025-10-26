# Datei-Dialoge Verbesserungen ✨

**Datum:** 7. Oktober 2025  
**Status:** ✅ KOMPLETT ÜBERARBEITET

## 🎯 Problem
Die alten Datei-Dialoge waren eine Katastrophe:
- ❌ Zu klein (900x600)
- ❌ Keine Mehrfachauswahl
- ❌ Keine Shortcuts zu wichtigen Orten
- ❌ Keine Dateigrößen-Anzeige
- ❌ Schlechte UX für forensische Arbeit

## ✅ Lösung: Professionelle Dialog-System

### 1. **ROOT-Auswahl** (`choose_root()`)
```
Größe: 1200x800 Pixel
Shortcuts: /, /home, /run/media, /mnt, /media
Features: Detail-Ansicht, große übersichtliche Darstellung
```

### 2. **Ordner hinzufügen** (`add_dir()`)
```
Größe: 1200x800 Pixel
Multi-Selektion: ✅ JA (Strg+Klick, Shift+Klick)
Shortcuts: /, /home, /run/media, /mnt, /media, /dev
Duplikat-Prüfung: ✅ Automatisch
Log-Ausgabe: ✅ "✓ Ziel hinzugefügt: ..."
Info-Label: Zeigt Tipp für Multi-Selektion
```

### 3. **Datei/Abbild hinzufügen** (`add_file()`)
```
Größe: 1200x800 Pixel
Multi-Selektion: ✅ JA (mehrere Images/Archive auf einmal)
Shortcuts: /, /home, /run/media, /mnt, /media
Dateigröße: ✅ Zeigt MB-Größe im Log
Filter: Disk-Images, Archive, Alle Dateien
Duplikat-Prüfung: ✅ Automatisch
Log-Ausgabe: ✅ "✓ Ziel hinzugefügt: file.iso (250.5 MB)"
```

### 4. **Device hinzufügen** (`add_dev()`)
```
Größe: 1200x800 Pixel
Multi-Selektion: ✅ JA (mehrere Devices)
Shortcuts: /dev, /dev/disk/by-id, /dev/disk/by-uuid, /dev/disk/by-label, /sys/block
Filter: Block-Devices (sd*, nvme*, mmcblk*, etc.)
Warnung: ⚠️ Rote Info-Box über Root-Rechte
Auto-Check: Prüft ob "Mit Root" + "Auto-Mount" aktiviert ist
Duplikat-Prüfung: ✅ Automatisch
```

### 5. **Scanner-Auswahl** (`choose_scanner()`)
```
Größe: 1200x800 Pixel
Start-Verzeichnis: ~/.local/share/wallet-gui/scripts/
Shortcuts: scripts/, wallet-gui/, /home
Filter: Shell-Skripte (.sh), Python (.py), Alle
Warnung: ⚠️ Gelbe Info-Box über standalone/-Scanner
Standalone-Check: Verhindert Auswahl von CLI-only Scannern
Log-Ausgabe: ✅ "✓ Custom-Scanner gewählt: ..."
```

## 🚀 Neue Features

### Multi-Selektion
- **Ordner:** Mehrere Ordner auf einmal hinzufügen
- **Dateien:** Mehrere Images/Archive auf einmal
- **Devices:** Mehrere Block-Devices auf einmal

### Intelligente Shortcuts
- **Forensik-relevant:** /run/media, /mnt, /media (gemountete Datenträger)
- **Device-Arbeit:** /dev/disk/by-label, /dev/disk/by-id (lesbare Namen)
- **System:** /, /home, /sys/block

### Visual Feedback
- ✅ **Grüne Häkchen** in Logs bei Erfolg
- ⚠️ **Warnungen** für kritische Operationen (Devices)
- 💡 **Tipps** für bessere Bedienung (Multi-Selektion)
- 📊 **Dateigrößen** bei Image-Hinzufügung

### Duplikat-Schutz
```python
if not self.targets.findItems(f, QtCore.Qt.MatchFlag.MatchExactly):
    self.targets.addItem(f)
```
Verhindert doppelte Einträge automatisch.

### Context-Aware Warnungen
- **Devices ohne Root:** Warnt wenn Root-Rechte fehlen
- **Standalone-Scanner:** Verhindert GUI-inkompatible Scanner
- **Dateigröße:** Zeigt MB-Größe für bessere Übersicht

## 📐 Design-Prinzipien

### Größe: 1200x800
```python
dialog.resize(1200, 800)
```
Groß genug für:
- Lange Pfade (/run/media/emil/MY_LONG_DISK_LABEL/...)
- Viele Dateien (forensische Archive mit 1000+ Einträgen)
- Detail-Ansicht mit Größen/Datum/Rechte

### Detail-Ansicht
```python
dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
```
Zeigt:
- Dateiname
- Größe
- Typ
- Änderungsdatum
- Berechtigungen

### Native Dialog: NEIN
```python
dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
```
Warum? Native Dialoge:
- Sind oft zu klein
- Haben keine Sidebar-URL-Unterstützung
- Sind schwer anpassbar
- Verhalten sich inkonsistent zwischen Systemen

## 🎨 Farbcodierung

### Blau (Info)
```css
background-color: #e3f2fd;
```
Verwendet für: Normale Hinweise, Tipps

### Gelb (Warnung)
```css
background-color: #fff3cd; border: 1px solid #ffc107;
```
Verwendet für: Wichtige Hinweise (Standalone-Scanner)

### Rot (Kritisch)
```css
background-color: #ffebee; border: 2px solid #f44336;
```
Verwendet für: Kritische Warnungen (Device-Scanning, Root-Rechte)

## 📊 Vorher/Nachher Vergleich

| Feature | Vorher ❌ | Nachher ✅ |
|---------|----------|-----------|
| Dialog-Größe | 900x600 | **1200x800** |
| Multi-Selektion | Nein | **Ja** |
| Shortcuts | Keine | **/run/media, /mnt, /dev/disk/...** |
| Dateigröße | Nicht angezeigt | **250.5 MB angezeigt** |
| Duplikat-Schutz | Nein | **Automatisch** |
| Log-Feedback | Minimal | **"✓ Ziel hinzugefügt: ..."** |
| Warnungen | Keine | **Context-aware (Devices, Standalone)** |
| Info-Labels | Keine | **Inline-Tipps im Dialog** |

## 🧪 Test-Szenario

### Bulk-Operation Test
1. **Mehrere Images hinzufügen:**
   ```
   Strg+Klick auf: backup1.img, backup2.img, backup3.img
   → Alle 3 werden hinzugefügt mit Größenangabe
   ```

2. **Mehrere Devices scannen:**
   ```
   In /dev/disk/by-label/:
   Strg+Klick auf: USB_DRIVE, BACKUP_DISK, OLD_HDD
   → Alle 3 werden hinzugefügt
   → Warnung wenn Root-Optionen fehlen
   ```

3. **Große Ordner-Strukturen:**
   ```
   1200x800 Dialog zeigt lange Pfade:
   /run/media/emil/MY_FORENSICS_BACKUP_2024_Q3/evidence/...
   ```

## ✨ Workflow-Verbesserung

### Alt (❌ Ineffizient)
```
1. Dialog öffnen (klein, 900x600)
2. Datei wählen
3. Dialog schließen
4. Dialog öffnen (wieder klein...)
5. Nächste Datei wählen
6. Dialog schließen
→ 5x für 5 Dateien! 😫
```

### Neu (✅ Effizient)
```
1. Dialog öffnen (groß, 1200x800)
2. Strg+Klick auf 5 Dateien
3. Dialog schließen
→ 1x für 5 Dateien! 🚀
```

**Zeitersparnis:** ~80% bei Bulk-Operationen

## 🔧 Code-Qualität

### Konsistenz
Alle Dialoge folgen dem gleichen Pattern:
```python
dialog.resize(1200, 800)
dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
dialog.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
dialog.setSidebarUrls(shortcuts)
```

### Fehlerbehandlung
```python
if f and not self.targets.findItems(f, QtCore.Qt.MatchFlag.MatchExactly):
    # Nur hinzufügen wenn nicht Duplikat
```

### User Feedback
```python
self.append_log(f"✓ Ziel hinzugefügt: {f} ({size_mb:.1f} MB)\n")
```

## 🎯 Forensik-Optimiert

### Typische Use-Cases
1. **USB-Stick-Forensik:** /dev/disk/by-label/USB_EVIDENCE
2. **Image-Analyse:** Mehrere .img/.iso Files auf einmal
3. **Archive-Scanning:** Bulk-Hinzufügen von .zip/.7z
4. **Device-Cloning:** Mehrere /dev/sdX Devices parallel

### Warum 1200x800?
- **Lange Pfade:** `/run/media/user/MY_VERY_LONG_DISK_LABEL_2024_BACKUP/forensics/evidence/case123/...`
- **Viele Einträge:** Archive mit 1000+ Dateien
- **Detail-Spalten:** Name + Größe + Datum + Typ = braucht Platz
- **Komfort:** Weniger Scrollen = schnellere Arbeit

## 🏆 Resultat

Die Datei-Dialoge sind jetzt:
- ✅ **Professionell:** Große, übersichtliche Darstellung
- ✅ **Effizient:** Multi-Selektion spart Zeit
- ✅ **Forensik-optimiert:** Shortcuts zu wichtigen Orten
- ✅ **User-friendly:** Inline-Tipps und Warnungen
- ✅ **Robust:** Duplikat-Schutz und Error-Handling

**Von Katastrophe zu Excellence! 🚀**
