# Schnellzugriff-Shortcuts in Dialogen 🎯

## ROOT-Auswahl
```
Sidebar:
├─ 📁 / (Root)
├─ 🏠 /home/emil
├─ 💾 /run/media
├─ 💿 /mnt
└─ 📀 /media
```

## Ordner hinzufügen
```
Sidebar:
├─ 📁 / (Root)
├─ 🏠 /home/emil
├─ 💾 /run/media (USB-Sticks, externe HDDs)
├─ 💿 /mnt (manuell gemountete Datenträger)
├─ 📀 /media
└─ 🖥️  /dev (Devices)
```

## Device hinzufügen
```
Sidebar:
├─ 🖥️  /dev
├─ 🔗 /dev/disk/by-id (z.B. usb-Samsung_SSD_850...)
├─ 🏷️  /dev/disk/by-uuid (z.B. 1234-5678...)
├─ 📛 /dev/disk/by-label (z.B. USB_BACKUP) ← EMPFOHLEN!
└─ 📊 /sys/block (sda, nvme0n1, ...)
```

## Scanner-Auswahl
```
Sidebar:
├─ 🔬 ~/.local/share/wallet-gui/scripts/
├─ 📦 ~/.local/share/wallet-gui/
└─ 🏠 /home/emil
```

## Warum by-label?

### ❌ Schlecht: /dev/sda
```bash
/dev/sda  # Ist das die externe Platte oder die interne SSD?
```

### ✅ Gut: /dev/disk/by-label/
```bash
/dev/disk/by-label/FORENSICS_BACKUP_2024
/dev/disk/by-label/EVIDENCE_USB
/dev/disk/by-label/OLD_LAPTOP_HDD
```

**Klar erkennbar was man scannt!**

## Multi-Selektion Tastatur-Shortcuts

```
Strg + Klick     →  Einzelne Dateien/Ordner hinzufügen
Shift + Klick    →  Bereich auswählen (von A bis Z)
Strg + A         →  Alles auswählen
```

## Beispiel-Workflow

### Mehrere USB-Sticks scannen:
```
1. "Device hinzufügen" klicken
2. Zu /dev/disk/by-label/ navigieren
3. Strg+Klick auf:
   - USB_STICK_1
   - USB_STICK_2
   - OLD_BACKUP
4. "Öffnen" → Alle 3 zur Liste hinzugefügt! ✓
```

### Mehrere Backup-Images:
```
1. "Datei/Abbild hinzufügen" klicken
2. Zu /run/media/emil/BACKUP/ navigieren
3. Shift+Klick: laptop_backup_2024-01.img bis laptop_backup_2024-12.img
4. "Öffnen" → 12 Images auf einmal hinzugefügt! ✓
```

## Zeitersparnis

| Aktion | Alt (5x öffnen) | Neu (1x öffnen + Multi) |
|--------|-----------------|-------------------------|
| 5 Images hinzufügen | ~45 Sekunden | ~8 Sekunden |
| 10 Ordner hinzufügen | ~90 Sekunden | ~12 Sekunden |
| 3 Devices hinzufügen | ~30 Sekunden | ~5 Sekunden |

**Durchschnittliche Zeitersparnis: 75-85%** 🚀
