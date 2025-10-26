# Wallet GUI - Scanner - Element-Erklärung 📋

**Basierend auf Screenshot vom 7. Oktober 2025**

## 🎯 Obere Zeile (Hauptkonfiguration)

### 1. **ROOT:** `/run/media/emil/DATEN`
```
Zweck: Arbeitsverzeichnis für Scanner-Output
Was passiert:
  - Hier wird der Ordner _logs/ erstellt
  - Scanner schreibt Ergebnisse nach: <ROOT>/_logs/walletscan_YYYYMMDD_HHMMSS/
  - Staging-Ordner (falls aktiviert): <ROOT>/Software/_staging_wallets/

Wann ändern:
  - Wenn Output woanders gespeichert werden soll
  - Standard: /run/media/emil/DATEN (gemountete Platte)
  
Tipp: Sollte auf schneller Platte liegen (nicht USB 2.0!)
```

### 2. **ROOT wählen...** Button
```
Zweck: ROOT-Verzeichnis ändern
Was passiert:
  - Öffnet kdialog (falls vorhanden) oder Qt-Dialog
  - Dialog-Größe: 1200x800
  - Shortcuts: /, /home, /run/media, /mnt, /media
  
Wann nutzen:
  - Vor dem ersten Scan
  - Wenn Output auf andere Platte soll
  - Wenn mehr Speicherplatz benötigt wird
```

### 3. **Scanner:** `wallet_harvest_any.sh` (Dropdown)
```
Zweck: Auswahl des Scanner-Skripts
Verfügbare Scanner:
  - wallet_harvest_any.sh (Standard)
  - hrm_swarm_scanner_wrapper.sh (mit Auto-Mount)
  - wallet_scan_archives.sh
  - wallet_scan_images.sh
  - Eigene Scanner (mit "Eigener Scanner..." hinzufügen)

Was ist der Unterschied:
  - wallet_harvest_any.sh: Legacy, manuelles Mount
  - hrm_swarm_scanner_wrapper.sh: Modern, Auto-Mount, HRM-Scoring
  - wallet_scan_archives.sh: Spezialisiert auf Archive
  - wallet_scan_images.sh: Spezialisiert auf Images

Empfehlung: hrm_swarm_scanner_wrapper.sh
```

### 4. **Eigener Scanner...** Button
```
Zweck: Custom Scanner-Skript hinzufügen
Was passiert:
  - Öffnet kdialog in ~/.local/share/wallet-gui/scripts/
  - Nur .sh und .py Dateien
  - Warnt vor standalone/-Scanner (nicht GUI-kompatibel!)
  
Wann nutzen:
  - Wenn eigenes Scanner-Skript vorhanden
  - Für Testing/Entwicklung
  - NICHT für standalone/hrm_swarm_scanner.py (CLI-only!)
```

---

## 📂 Mittlere Zeile (Target-Liste)

### 5. **Große leere Liste**
```
Zweck: Zeigt alle Scan-Targets an
Inhalt:
  - Ordner: /path/to/directory
  - Dateien: /path/to/file.img
  - Devices: /dev/sda1 oder /dev/disk/by-label/USB_STICK
  - Archive: /path/to/backup.zip

Multi-Selektion:
  - Strg+Klick: Einzelne Targets wählen
  - Shift+Klick: Bereich wählen
  - Für "Auswahl entfernen"
```

---

## 🔘 Rechte Buttons (Target-Management)

### 6. **Ordner hinzufügen** Button
```
Zweck: Verzeichnis(se) zur Scan-Liste hinzufügen
Was passiert:
  - Öffnet kdialog (Multi-Selektion!)
  - Startet in: <ROOT> oder /run/media
  - Erlaubt: Mehrere Ordner mit Strg+Klick
  - Duplikat-Schutz: Keine doppelten Einträge
  - Log: "✓ Ordner hinzugefügt: /path"

Scanner-Verhalten:
  → Rekursive Datei-Enumeration
  → Alle Dateien <= 512 MB werden gescannt
  → Dateien > 512 MB werden ÜBERSPRUNGEN
  
Wann nutzen:
  - Normale Ordner mit vielen Dateien
  - /home/user/Documents
  - Gemountete Verzeichnisse
  
NICHT für:
  - Große Image-Dateien (nutze "Datei/Abbild hinzufügen")
```

### 7. **Datei/Abbild hinzufügen** Button
```
Zweck: Einzelne Datei(en) zur Scan-Liste hinzufügen
Was passiert:
  - Öffnet kdialog mit Filter
  - Multi-Selektion möglich!
  - Filter: *.img, *.iso, *.zip, *.7z, *.tar, etc.
  - Zeigt Dateigröße im Log: "✓ Datei hinzugefügt: file.img (250.5 MB)"

Scanner-Verhalten:
  → Images (.img, .iso, .dd): Auto-Mount + Inhalt scannen
  → Archive (.zip, .7z, .tar): Auto-Extract + Inhalt scannen
  → Reguläre Dateien: Content-Scan (wenn <= 512 MB)
  
Wann nutzen:
  - ✅ Große Image-Dateien (> 512 MB)
  - ✅ ISO-Files
  - ✅ Archive (zip, 7z, tar)
  - ✅ Einzelne große Dateien
  
WICHTIG:
  Für deine 233 GB .img Datei → DIESEN Button nutzen!
  + "Mit Root (pkexec)" aktivieren
  + "Auto-Mount" aktivieren
```

### 8. **Device (/dev/...) hinzufügen** Button
```
Zweck: Block-Device zur Scan-Liste hinzufügen
Was passiert:
  - Öffnet kdialog in /dev/disk/by-label/ (empfohlen!)
  - Multi-Selektion möglich
  - Warnung wenn Root-Rechte fehlen
  
Scanner-Verhalten:
  → Device wird read-only gemountet
  → Mount-Punkt wird gescannt
  → Cleanup automatisch
  
Wann nutzen:
  - USB-Sticks: /dev/disk/by-label/USB_BACKUP
  - Externe HDDs: /dev/disk/by-label/FORENSICS
  - Partitionen: /dev/sda1, /dev/nvme0n1p2
  
WICHTIG:
  ✓ "Mit Root (pkexec)" MUSS aktiviert sein!
  ✓ "Auto-Mount" MUSS aktiviert sein!
```

### 9. **Auswahl entfernen** Button
```
Zweck: Gewählte Targets aus Liste löschen
Was passiert:
  - Entfernt alle selektierten Einträge
  - Keine Bestätigung (direkt gelöscht)
  
Workflow:
  1. Target(s) in Liste anklicken (Strg+Klick für mehrere)
  2. "Auswahl entfernen" klicken
  3. Weg!
```

### 10. **Liste leeren** Button
```
Zweck: ALLE Targets aus Liste löschen
Was passiert:
  - Löscht komplette Target-Liste
  - Keine Bestätigung (direkt gelöscht)
  
Wann nutzen:
  - Neu anfangen
  - Nach einem Scan
  - Wenn versehentlich viel hinzugefügt
```

---

## ⚙️ Optionen (Checkboxen)

### 11. **☐ Aggressiv**
```
Zweck: Intensiverer Scan mit mehr Features
Was ändert sich:
  ✓ Threads: 10 (statt 6)
  ✓ Max Dateigröße: 1024 MB = 1 GB (statt 512 MB)
  ✓ YARA-Scan aktiviert
  ✓ Mehr Dateitypen durchsucht
  
Nachteile:
  ⚠ Langsamer (mehr Dateien)
  ⚠ Mehr RAM-Verbrauch
  ⚠ Mehr CPU-Last
  
Wann aktivieren:
  - Wenn gründlicher Scan gewünscht
  - Wenn Zeit keine Rolle spielt
  - Bei wichtigen/verdächtigen Daten
  
Wann NICHT aktivieren:
  - Schneller Probe-Scan
  - Schwache Hardware
  - Große Datenmengen (> 1 TB)
```

### 12. **☐ Staging anlegen (Symlinks)**
```
Zweck: Symlinks aller Treffer erstellen
Was passiert:
  → Scanner erstellt: <ROOT>/Software/_staging_wallets/
  → Für jeden Treffer: Symlink zur Original-Datei
  → Struktur: _staging_wallets/<filename>_<hash>
  
Vorteile:
  ✓ Schneller Zugriff auf alle Funde
  ✓ Original-Dateien bleiben unverändert
  ✓ Einfach zu durchsuchen
  
Wann aktivieren:
  - Wenn viele Treffer erwartet werden
  - Für manuelle Nachbearbeitung
  - Zum Sammeln von Fundstellen
  
Hinweis:
  Braucht Speicherplatz für Symlinks (minimal)
```

### 13. **☐ Mit Root (pkexec) für Auto-Mount**
```
Zweck: Scanner mit Root-Rechten ausführen
Was ermöglicht das:
  ✓ Images mounten (losetup, mount)
  ✓ Devices mounten (/dev/sdX)
  ✓ Archive mit privilegierten Rechten entpacken
  ✓ Zugriff auf geschützte Dateien
  
Was passiert:
  → pkexec-Passwort-Dialog erscheint
  → Scanner läuft mit sudo-Rechten
  → Cleanup läuft auch mit Root
  
Wann AKTIVIEREN:
  ✅ Images scannen (.img, .iso, .dd)
  ✅ Devices scannen (/dev/sdX)
  ✅ Auto-Mount nutzen
  
Wann NICHT aktivieren:
  ❌ Nur normale Ordner scannen
  ❌ Bereits gemountete Verzeichnisse
  ❌ Sicherheitsbedenken

WICHTIG für deine .img Datei:
  → MUSS aktiviert sein!
```

### 14. **☑ Auto-Mount für Images/Devices**
```
Zweck: Automatisches Mounten von Images/Devices
Was passiert:
  → Images (.img, .iso, .dd): Werden read-only gemountet
  → Archive (.zip, .7z, .tar): Werden entpackt
  → Devices (/dev/sdX): Werden read-only gemountet
  → Nach Scan: Automatisches Unmount/Cleanup
  
Ohne Auto-Mount:
  → Images werden als Datei gescannt (sinnlos bei 233 GB!)
  → Devices können nicht gescannt werden
  → Archive werden nicht entpackt
  
Wann AKTIVIEREN:
  ✅ IMMER wenn Images/Devices gescannt werden!
  ✅ Bei Archive-Scanning
  ✅ Standard: AN lassen!
  
Wann DEAKTIVIEREN:
  ❌ Nur bei bereits gemounteten Verzeichnissen
  ❌ Wenn nur reguläre Dateien gescannt werden
  
WICHTIG für deine .img Datei:
  → MUSS aktiviert sein!
  → Sonst wird .img übersprungen (zu groß!)
```

---

## 🔵 Utility-Buttons (Untere Zeile)

### 15. **ROOT in Dolphin** Button
```
Zweck: ROOT-Verzeichnis in Dolphin öffnen
Was passiert:
  → dolphin /run/media/emil/DATEN
  → Öffnet Dateimanager im ROOT-Ordner
  
Wann nutzen:
  - Vor dem Scan: Ordner-Struktur prüfen
  - Nach dem Scan: Ergebnisse durchsuchen
  - _logs/ Ordner ansehen
```

### 16. **Staging öffnen** Button
```
Zweck: Staging-Ordner in Dolphin öffnen
Was passiert:
  → dolphin <ROOT>/Software/_staging_wallets/
  → Zeigt alle Symlinks zu Treffern
  
Wann nutzen:
  - Nach Scan mit "Staging anlegen"
  - Um Treffer schnell zu durchsuchen
  - Für manuelle Nachbearbeitung
  
Hinweis:
  Nur sinnvoll wenn "Staging anlegen" aktiviert war!
```

### 17. **Logs öffnen** Button
```
Zweck: Log-Verzeichnis in Dolphin öffnen
Was passiert:
  → Öffnet letztes Scan-Output-Verzeichnis
  → Oder: <ROOT>/_logs/ falls kein Scan lief
  
Inhalt:
  - hits.txt (Alle Treffer)
  - mnemonic_raw.txt (Seed-Kandidaten)
  - scan.log (Scanner-Output)
  - summary.json (Statistiken)
  
Wann nutzen:
  - Nach jedem Scan!
  - Um Ergebnisse zu prüfen
  - Bei Fehlersuche
```

### 18. **📖 Hilfe** Button (blau)
```
Zweck: Interaktive Hilfe öffnen
Was passiert:
  → Öffnet MANUAL_INTERACTIVE.html im Browser
  → Zeigt ausführliche Anleitung
  
Inhalt:
  - Bedienungsanleitung
  - Scanner-Optionen erklärt
  - Troubleshooting
  - Beispiele
```

---

## 🚀 Action-Buttons

### 19. **Scan starten** Button (grün)
```
Zweck: Scanner-Prozess starten
Was passiert:
  1. Prüft ob Targets vorhanden
  2. Erstellt Output-Verzeichnis
  3. Startet Scanner (evtl. mit pkexec)
  4. Zeigt Live-Output im "Live-Log" Tab
  5. Auto-Load von Ergebnissen nach Scan
  
Aktiviert/Deaktiviert:
  - Während Scan: DEAKTIVIERT
  - Nach Scan: Wieder AKTIVIERT
  
Workflow:
  → Targets hinzufügen
  → Optionen wählen
  → "Scan starten" klicken
  → Im "Live-Log" Tab zuschauen
  → Warten...
  → "Hits" Tab prüfen!
```

### 20. **Stop** Button (rot, deaktiviert)
```
Zweck: Laufenden Scan abbrechen
Was passiert:
  → Sendet SIGTERM an Scanner-Prozess
  → Cleanup wird ausgeführt
  → Partial Ergebnisse bleiben erhalten
  
Aktiviert:
  - Nur während Scan läuft
  
Wann nutzen:
  - Scan dauert zu lange
  - Falsche Targets gewählt
  - System überlastet
  
Hinweis:
  Ergebnisse bis zum Abbruch bleiben!
```

---

## 📊 Tab-Leiste

### 21. **Live-Log** Tab
```
Zweck: Scanner-Output in Echtzeit anzeigen
Inhalt:
  - Scanner-Meldungen
  - Fortschritt
  - Fehler/Warnungen
  - Mount/Unmount-Aktionen
  
Features:
  ✓ Auto-Scroll (scrollt automatisch mit)
  ✓ Timer unten (Elapsed-Zeit)
  ✓ Status-Label ("Bereit", "Läuft...", "Fertig")
```

### 22. **Hits** Tab
```
Zweck: Gefundene Treffer anzeigen
Inhalt:
  - Datei:Zeile:Snippet für jeden Treffer
  - Filterable (Regex)
  - Sortierbar
  
Features:
  ✓ Regex-Filter: bc1|0x|xpub
  ✓ "Öffnen" Button: Datei im Editor öffnen
  ✓ "Export .tsv": Alle Treffer exportieren
  ✓ "Kopieren": Treffer in Zwischenablage
```

### 23. **Mnemonics** Tab
```
Zweck: Seed-Phrase-Kandidaten anzeigen
Inhalt:
  - 12/24 Wort-Kombinationen
  - Heuristische Erkennung
  
Format:
  # Datei: /path/to/file
  word1 word2 word3 ... word12
```

### 24. **Anleitung** Tab
```
Zweck: Eingebaute Hilfe anzeigen
Inhalt:
  - Kurz-Anleitung
  - Button-Erklärungen
  - Workflow-Tipps
```

---

## 💡 Hinweis-Bereich (unten im Screenshot)

### 25. **Hinweis-Text**
```
"Hinweis: Empfohlene Pakete: python3-pyqt6 kdialog p7zip 
         p7zip-plugins sleuthkit ntfs-3g"
         
Zweck: Zeigt empfohlene Dependencies
Warum wichtig:
  - kdialog: Für native KDE-Dialoge
  - p7zip: Für Archive-Extraktion
  - sleuthkit: Für forensische Image-Analyse
  - ntfs-3g: Für NTFS-Dateisystem-Support
```

### 26. **🔍 FSearch öffnen: ROOT-Verzeichnis auswählen**
```
Zweck: Log-Meldung von Button-Klick
Zeigt:
  - Welche Aktion gerade läuft
  - Startpfad für Dialog
  - Tipps zur Bedienung
```

### 27. **Startpfad: /run/media/emil/DATEN**
```
Zweck: Info wo Dialog startet
```

### 28. **💡 Tipp: Doppelklick auf Ordner um auszuwählen**
```
Zweck: Inline-Hilfe für Benutzer
```

### 29. **× Abgebrochen**
```
Zweck: Status-Meldung
Zeigt: Dialog wurde ohne Auswahl geschlossen
```

---

## 🎯 Status-Leiste (ganz unten)

### 30. **"Bereit"**
```
Zweck: Scanner-Status anzeigen
Mögliche Werte:
  - "Bereit" → Kein Scan läuft
  - "Läuft... (XX:XX)" → Scan aktiv mit Timer
  - "Fertig (XX:XX | YY Treffer)" → Scan beendet
  - "Fehler: ..." → Problem aufgetreten
```

---

## 🎨 Zusammenfassung: Farbcodierung

```
Blau (#4fc3f7):  Hilfe-Button (wichtig!)
Grün:             Scan starten (Action)
Rot:              Stop (Abbruch)
Grau:             Deaktivierte Buttons
Schwarz:          Haupt-UI (Dark Theme)
```

---

## 🔥 Dein konkreter Use-Case

**Für deine 233 GB .img Datei:**

```
1. ROOT: /run/media/emil/DATEN (bereits okay!)
2. Scanner: wallet_harvest_any.sh ÄNDERN zu:
   → hrm_swarm_scanner_wrapper.sh (für Auto-Mount!)
3. "Datei/Abbild hinzufügen" klicken
4. volume_disk_2025-10-06-1346.img auswählen
5. ☑ Mit Root (pkexec) aktivieren
6. ☑ Auto-Mount aktivieren  
7. Optional: ☐ Aggressiv (für gründlicheren Scan)
8. "Scan starten" klicken
9. Im "Live-Log" Tab zuschauen
10. Nach Scan: "Hits" Tab prüfen!
```

---

**Alle Buttons erklärt! 🎉**
