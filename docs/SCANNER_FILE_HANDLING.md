# Scanner-Verhalten: Was wird gescannt? 📋

## 🎯 Problem: "Welche Dateien werden gescannt?"

### Aktuelle Situation:
1. **Scanner erhält:** Ordner oder Dateien
2. **Scanner verhält sich unterschiedlich:**
   - **Ordner** → Rekursive Datei-Enumeration (alle Dateien bis 512 MB)
   - **Image-Datei (.img, .iso, etc.)** → Auto-Mount + Scan des Inhalts
   - **Archiv (.zip, .7z, etc.)** → Extrahiert + Scan
   - **Device (/dev/sdX)** → Mount + Scan

## 📂 Ordner-Scanning

```python
def enumerate_files(root, max_mb=256):
    # Durchläuft ALLE Dateien rekursiv
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            if os.path.getsize(fp) <= max_mb * 1024 * 1024:
                # Scanne diese Datei
```

**Dateigröße-Limit:**
- Normal: 512 MB
- Aggressiv: 1024 MB (1 GB)

**Dateien die übersprungen werden:**
- Größer als Limit (z.B. 233 GB .img Datei!)
- In Exclude-Pattern (z.B. `.git`, `node_modules`)

## 🖼️ Image-Scanning (.img, .iso, etc.)

**Wenn eine IMAGE-DATEI angegeben wird:**

```bash
# Wrapper erkennt: volume_disk_2025-10-06-1346.img
if [[ "$target" =~ \.(img|iso|dd|bin|raw)$ ]]; then
    mount_image "$target"  # Auto-Mount!
fi
```

**Was passiert:**
1. Image wird read-only gemountet
2. Mount-Punkt wird zum neuen Target
3. Scanner scannt den INHALT des Images
4. Cleanup am Ende

**Wichtig:** Die .img Datei selbst wird **NICHT** content-gescannt (zu groß!), sondern **gemountet**!

## 📦 Archive-Scanning (.zip, .7z, etc.)

```bash
if [[ "$target" =~ \.(zip|tar|7z|rar)$ ]]; then
    extract_archive "$target"  # Auto-Extract!
fi
```

**Was passiert:**
1. Archiv wird nach /tmp/wallet_extract_XXX/ extrahiert
2. Extract-Verzeichnis wird zum neuen Target
3. Scanner scannt alle Dateien im Archiv
4. Cleanup am Ende

## 🔧 Was aktuell schief läuft

### Szenario: /mnt/mediacenter1/sido/

**Ordner-Inhalt:**
```
volume_disk_2025-10-06-1346.img  → 233 GB (!)
volume_disk_2025-10-06-1346.log  → 419 B
volume_parttbl_2025-10-06-1346.txt → 0 B
```

**Wenn du den ORDNER hinzufügst:**
```
→ enumerate_files("/mnt/mediacenter1/sido/")
  - .img wird ÜBERSPRUNGEN (233 GB > 512 MB Limit!)
  - .log wird gescannt (419 B, okay)
  - .txt wird gescannt (0 B, okay)

Ergebnis: NUR .log und .txt werden gescannt!
```

**Wenn du die IMAGE-DATEI hinzufügst:**
```
→ Auto-Mount aktiviert
  - .img wird GEMOUNTET (nicht content-gescannt!)
  - Mount-Punkt: /tmp/wallet_mount_XXX/
  - Scanner scannt INHALT des gemounteten Images
  
Ergebnis: Der INHALT des Images wird gescannt!
```

## ✅ Lösung: Richtige Targets wählen

### Für große Images:
```
❌ FALSCH: Ordner hinzufügen (/mnt/mediacenter1/sido/)
✅ RICHTIG: Datei hinzufügen (volume_disk_2025-10-06-1346.img)
```

### Für Ordner mit vielen Dateien:
```
✅ RICHTIG: Ordner hinzufügen (/home/user/documents/)
→ Alle Dateien bis 512 MB werden gescannt
```

### Für Archive:
```
✅ RICHTIG: Datei hinzufügen (backup.zip)
→ Wird extrahiert und Inhalt gescannt
```

## 🎛️ Aggressiv-Modus

**Normal (512 MB Limit):**
```
- Kleine/mittlere Dateien: ✅ Gescannt
- Große Dateien (> 512 MB): ❌ Übersprungen
```

**Aggressiv (1024 MB = 1 GB Limit):**
```
- Kleine/mittlere Dateien: ✅ Gescannt
- Große Dateien (> 1 GB): ❌ Übersprungen
- Aber: Mehr Dateitypen, YARA aktiviert
```

## 📝 Dateitypen die gescannt werden

**Content-Scan (Text-Suche):**
```
Alle Dateien ohne Extension-Filter!
→ .txt, .json, .xml, .html, .js, .py, .log, .conf, ...
→ Auch: Binärdateien werden gescannt (mit -a Flag)
```

**ABER: Nur bis Größenlimit!**

## 🔍 Scanner-Logik zusammengefasst

```
IF Target ist Datei:
    IF Target endet mit .img/.iso/etc.:
        → Auto-Mount (mit Root-Rechten)
        → Scanne Mount-Punkt
    
    ELIF Target endet mit .zip/.7z/etc.:
        → Auto-Extract
        → Scanne Extract-Verzeichnis
    
    ELIF Dateigröße <= 512 MB:
        → Content-Scan (ripgrep/grep)
    
    ELSE:
        → Übersprungen (zu groß!)

ELIF Target ist Ordner:
    → enumerate_files() rekursiv
    → Jede Datei <= 512 MB wird gescannt

ELIF Target ist Device (/dev/sdX):
    → Auto-Mount (braucht Root!)
    → Scanne Mount-Punkt
```

## 🎯 Dein konkreter Fall

**Du hast:**
```
/mnt/mediacenter1/sido/volume_disk_2025-10-06-1346.img (233 GB)
```

**Was du tun musst:**

### Option 1: Image scannen (empfohlen)
```
1. "Datei/Abbild hinzufügen" klicken
2. volume_disk_2025-10-06-1346.img auswählen
3. "Mit Root (pkexec)" aktivieren
4. "Auto-Mount" aktivieren
5. Scan starten
→ Image wird gemountet, Inhalt wird gescannt!
```

### Option 2: Gemountetes Image-Verzeichnis scannen
```
# Erst manuell mounten:
$ sudo mkdir /mnt/sido_mount
$ sudo mount -o loop,ro /mnt/mediacenter1/sido/volume_disk_2025-10-06-1346.img /mnt/sido_mount

# Dann in GUI:
1. "Ordner hinzufügen" klicken
2. /mnt/sido_mount auswählen
3. Scan starten (OHNE Root, OHNE Auto-Mount)
→ Direkter Scan des gemounteten Inhalts
```

### Option 3: Nur die kleinen Dateien scannen
```
1. "Ordner hinzufügen" klicken
2. /mnt/mediacenter1/sido/ auswählen
3. Scan starten
→ Nur .log und .txt werden gescannt (nicht das Image!)
```

## 📊 Zusammenfassung

| Target-Typ | Verhalten | Empfehlung |
|------------|-----------|------------|
| **Große .img Datei (> 512 MB)** | ❌ Content-Scan: übersprungen<br>✅ Auto-Mount: gemountet+gescannt | Datei hinzufügen + Auto-Mount! |
| **Ordner mit .img** | ❌ .img übersprungen<br>✅ Andere Dateien gescannt | Besser: .img direkt hinzufügen |
| **Ordner mit .txt/.bin** | ✅ Alle Dateien <= 512 MB gescannt | Ordner hinzufügen ist okay |
| **Archive (.zip)** | ✅ Extrahiert + Inhalt gescannt | Datei hinzufügen |
| **Devices (/dev/sdX)** | ✅ Gemountet + Inhalt gescannt | Device hinzufügen + Root |

## 🚨 Wichtig!

**Für große Image-Dateien:**
- ✅ **IMMER** die Datei direkt hinzufügen (nicht den Ordner!)
- ✅ **IMMER** "Mit Root (pkexec)" aktivieren
- ✅ **IMMER** "Auto-Mount" aktivieren

**Sonst wird das Image übersprungen!**
