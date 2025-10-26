# Scanner-Strategie: Konsolidierung vs. Beibehaltung

## Aktuelle Situation

### Vorhandene Scanner:

1. **wallet_harvest_any.sh** (221 Zeilen)
   - ✅ Auto-Mount für Images & Devices
   - ✅ Kandidaten-Vorauswahl (find)
   - ✅ ripgrep/grep Pattern-Suche
   - ✅ Live-Output
   - ⚠️ Kein Scoring
   - ⚠️ Keine Validierung

2. **wallet_scan_images.sh** (50 Zeilen)
   - ✅ Spezialisiert auf ISO/IMG/DMG/VHD
   - ✅ Automatisches Loop-Mount
   - ⚠️ Ruft wallet_harvest_any.sh auf (Duplikation)

3. **wallet_scan_archives.sh** (50 Zeilen)
   - ✅ Spezialisiert auf ZIP/RAR/7Z/TAR
   - ✅ Automatisches Entpacken
   - ⚠️ Ruft wallet_harvest_any.sh auf (Duplikation)

4. **hrm_swarm_scanner.py** (328 Zeilen)
   - ✅ Scoring-System (1-15 Punkte)
   - ✅ Checksum-Validierung (Base58, Bech32)
   - ✅ YARA-Integration
   - ✅ HRM-Policy (adaptive Eskalation)
   - ✅ ThreadPoolExecutor
   - ✅ JSON-Output
   - ❌ Kein Auto-Mount
   - ❌ Kein Live-Output

---

## Empfehlung: **HYBRID-ANSATZ** 🎯

### Strategie: HRM als Kern + Auto-Mount Extension

**Begründung:**
1. **HRM Scanner ist technisch überlegen** (Scoring, Validierung, YARA)
2. **Auto-Mount ist das einzige fehlende Feature**
3. **Wrapper-Erweiterung ist einfacher als komplette Scanner-Neuentwicklung**
4. **Bestehende Scanner haben viel Bash-Logik für Mounting**

### Lösung: Erweiterter Wrapper

```
hrm_swarm_scanner_wrapper.sh (erweitert)
├── Pre-Processing: Auto-Mount Logic
│   ├── Images (ISO, IMG, DMG, VHD) → losetup + mount
│   ├── Archives (ZIP, TAR, 7Z) → temp extract
│   └── Devices (/dev/sdX) → mount read-only
│
├── HRM Scanner Execution
│   └── python3 hrm_swarm_scanner.py
│
└── Post-Processing
    ├── JSON → GUI-Format Konvertierung
    ├── Staging-Symlinks erstellen
    └── Cleanup (Unmount, Temp-Files)
```

---

## Implementierung: Phase 1 - Auto-Mount

### Erweitere den Wrapper um Auto-Mount:

```bash
# In hrm_swarm_scanner_wrapper.sh

# Phase 1: Auto-Mount & Target-Preparation
REAL_TARGETS=()
MOUNTS=()
LOOPS=()
TEMP_DIRS=()

for target in "${TARGETS[@]}"; do
  if [[ $AUTO_MOUNT -eq 1 ]]; then
    # Image-Datei?
    if [[ -f "$target" ]] && [[ "$target" =~ \.(img|iso|dd|dmg|vhd|vhdx)$ ]]; then
      mount_image "$target"  # → REAL_TARGETS, MOUNTS, LOOPS
    
    # Archiv?
    elif [[ -f "$target" ]] && [[ "$target" =~ \.(zip|tar|7z|rar|tgz)$ ]]; then
      extract_archive "$target"  # → REAL_TARGETS, TEMP_DIRS
    
    # Device?
    elif [[ -b "$target" ]]; then
      mount_device "$target"  # → REAL_TARGETS, MOUNTS
    
    # Reguläres Verzeichnis
    else
      REAL_TARGETS+=("$target")
    fi
  else
    REAL_TARGETS+=("$target")
  fi
done

# Phase 2: HRM Scanner mit vorbereiteten Targets
python3 hrm_swarm_scanner.py --target "${REAL_TARGETS[@]}" ...

# Phase 3: Cleanup
cleanup_mounts
cleanup_temp_dirs
```

**Vorteil:** Alle Auto-Mount-Logik an einem Ort, HRM Scanner bleibt clean.

---

## Plan: Scanner-Konsolidierung

### Option A: ✅ **EMPFOHLEN - Hybrid**

**Behalten:**
- `hrm_swarm_scanner.py` (standalone, core engine)
- `hrm_swarm_scanner_wrapper.sh` (erweitert mit Auto-Mount)

**Archivieren** (optional behalten für Spezialfälle):
- `wallet_harvest_any.sh` → `scripts/legacy/`
- `wallet_scan_images.sh` → `scripts/legacy/`
- `wallet_scan_archives.sh` → `scripts/legacy/`

**GUI zeigt:**
```
Scanner: [▼]
  ├── HRM Swarm Scanner (empfohlen) ⭐
  ├── HRM Swarm Scanner (legacy-mode)
  └── Legacy Scanner (wallet_harvest_any.sh)
```

### Option B: Vollständige Konsolidierung

**Ein einziger Scanner:**
- `unified_wallet_scanner.sh`
- Integriert: Auto-Mount, Archive, HRM-Engine, Staging

**Nachteil:** Sehr komplex, schwer wartbar.

### Option C: Status Quo

**Alles behalten:**
- Nutzer wählen je nach Bedarf
- Mehr Flexibilität, aber Verwirrung

**Nachteil:** Code-Duplikation, inkonsistente Ergebnisse.

---

## Entscheidungsmatrix

| Kriterium | Option A (Hybrid) | Option B (Unified) | Option C (Status Quo) |
|-----------|-------------------|--------------------|-----------------------|
| **Wartbarkeit** | ✅ Gut | ⚠️ Komplex | ❌ Duplikation |
| **Features** | ✅ Alle | ✅ Alle | ⚠️ Fragmentiert |
| **Performance** | ✅ Optimal | ✅ Optimal | ⚠️ Variiert |
| **Benutzerfreundlichkeit** | ✅ Ein Scanner | ✅ Ein Scanner | ❌ Verwirrend |
| **Backward-Compat** | ✅ Legacy verfügbar | ❌ Breaking | ✅ Ja |
| **Aufwand** | ⚠️ Mittel | ❌ Hoch | ✅ Minimal |

**Gewinner: Option A (Hybrid-Ansatz)** 🏆

---

## Implementierungsplan

### Phase 1: Auto-Mount im Wrapper (JETZT)

**Datei:** `scripts/hrm_swarm_scanner_wrapper.sh`

**Neue Funktionen:**
```bash
mount_image() {
  local img="$1"
  local dev=$(losetup --read-only --find --show -P "$img")
  # Mount alle Partitionen
  # Füge zu REAL_TARGETS hinzu
}

extract_archive() {
  local arch="$1"
  local tmpdir=$(mktemp -d)
  7z x "$arch" -o"$tmpdir"
  REAL_TARGETS+=("$tmpdir")
  TEMP_DIRS+=("$tmpdir")
}

mount_device() {
  local dev="$1"
  # Mount read-only
  # Füge zu REAL_TARGETS hinzu
}

cleanup() {
  # Unmount all
  # Remove temp dirs
  # Free loop devices
}
```

**Test:**
```bash
scripts/hrm_swarm_scanner_wrapper.sh \
  /run/media/emil/DATEN \
  --auto-mount \
  /run/media/emil/DATEN/backup.iso \
  /run/media/emil/DATEN/archive.zip
```

### Phase 2: GUI-Integration (NACH Phase 1)

**Dropdown-Eintrag:**
```
Scanner: [▼]
  ├── HRM Swarm Scanner (Standard) ⭐
  ├── Wallet Harvest (Legacy)
  └── [Separator]
  └── Nur Images scannen
  └── Nur Archive scannen
```

**Empfehlung:**
```
# Bei Auto-Mount aktiviert + Images/Archives:
→ Automatisch HRM Swarm Scanner wählen
```

### Phase 3: Legacy-Migration (OPTIONAL)

**Verschiebe alte Scanner:**
```bash
mkdir -p scripts/legacy
mv scripts/wallet_harvest_any.sh scripts/legacy/
mv scripts/wallet_scan_images.sh scripts/legacy/
mv scripts/wallet_scan_archives.sh scripts/legacy/
```

**GUI-Optionen:**
```
☐ Legacy-Scanner anzeigen (Erweitert)
```

---

## Auto-Mount Code-Vorlage

### Für hrm_swarm_scanner_wrapper.sh:

```bash
#!/usr/bin/env bash
# hrm_swarm_scanner_wrapper.sh v2.0
# MIT Auto-Mount-Unterstützung

# ... [Bestehender Code bis TARGETS] ...

# === AUTO-MOUNT LOGIC ===
REAL_TARGETS=()
MOUNTS=()
LOOPS=()
TEMP_DIRS=()
MOUNT_BASE="$ROOT/_mount/hrm_scan_$$"

mount_image() {
  local img="$1"
  echo ">>> Auto-Mount Image: $img"
  
  # Loop device erstellen
  local dev=$(sudo losetup --read-only --find --show -P "$img" 2>/dev/null || true)
  if [[ -z "$dev" ]]; then
    echo "  ✗ Konnte Loop-Device nicht erstellen"
    return 1
  fi
  LOOPS+=("$dev")
  
  # Partitionen finden
  local parts=$(lsblk -nrpo NAME,TYPE "$dev" 2>/dev/null | awk '$2=="part"{print $1}')
  if [[ -z "$parts" ]]; then
    parts="$dev"  # Keine Partitionen, Device selbst mounten
  fi
  
  # Jede Partition mounten
  local idx=0
  while read -r part; do
    [[ -z "$part" ]] && continue
    local mp="$MOUNT_BASE/$(basename "$img")_p${idx}"
    mkdir -p "$mp"
    
    if sudo mount -o ro "$part" "$mp" 2>/dev/null; then
      echo "  ✓ Gemountet: $part → $mp"
      REAL_TARGETS+=("$mp")
      MOUNTS+=("$mp")
    else
      echo "  ⚠ Konnte $part nicht mounten"
      rmdir "$mp" 2>/dev/null || true
    fi
    ((idx++))
  done <<< "$parts"
}

extract_archive() {
  local arch="$1"
  echo ">>> Auto-Extract Archive: $arch"
  
  local tmpdir=$(mktemp -d -p "$ROOT/_mount" "hrm_extract_XXXXXX")
  TEMP_DIRS+=("$tmpdir")
  
  # Versuche verschiedene Entpacker
  if command -v 7z &>/dev/null; then
    if 7z x -y -o"$tmpdir" "$arch" &>/dev/null; then
      echo "  ✓ Entpackt mit 7z"
      REAL_TARGETS+=("$tmpdir")
      return 0
    fi
  fi
  
  if [[ "$arch" =~ \.zip$ ]] && command -v unzip &>/dev/null; then
    if unzip -q "$arch" -d "$tmpdir" 2>/dev/null; then
      echo "  ✓ Entpackt mit unzip"
      REAL_TARGETS+=("$tmpdir")
      return 0
    fi
  fi
  
  if command -v tar &>/dev/null; then
    if tar -xf "$arch" -C "$tmpdir" 2>/dev/null; then
      echo "  ✓ Entpackt mit tar"
      REAL_TARGETS+=("$tmpdir")
      return 0
    fi
  fi
  
  echo "  ✗ Konnte Archiv nicht entpacken"
  rmdir "$tmpdir" 2>/dev/null || true
}

mount_device() {
  local dev="$1"
  echo ">>> Auto-Mount Device: $dev"
  
  # Partitionen prüfen
  local parts=$(lsblk -nrpo NAME,TYPE "$dev" 2>/dev/null | awk '$2=="part"{print $1}')
  if [[ -z "$parts" ]]; then
    parts="$dev"
  fi
  
  local idx=0
  while read -r part; do
    [[ -z "$part" ]] && continue
    local mp="$MOUNT_BASE/$(basename "$dev")_p${idx}"
    mkdir -p "$mp"
    
    if sudo mount -o ro "$part" "$mp" 2>/dev/null; then
      echo "  ✓ Gemountet: $part → $mp"
      REAL_TARGETS+=("$mp")
      MOUNTS+=("$mp")
    else
      echo "  ⚠ Konnte $part nicht mounten"
      rmdir "$mp" 2>/dev/null || true
    fi
    ((idx++))
  done <<< "$parts"
}

cleanup_mounts() {
  echo ">>> Cleanup..."
  
  # Unmount
  for mp in "${MOUNTS[@]}"; do
    sudo umount "$mp" 2>/dev/null && echo "  ✓ Unmount: $mp"
    rmdir "$mp" 2>/dev/null || true
  done
  
  # Loop devices freigeben
  for loop in "${LOOPS[@]}"; do
    sudo losetup -d "$loop" 2>/dev/null && echo "  ✓ Loop freigegeben: $loop"
  done
  
  # Temp-Verzeichnisse löschen
  for tmpdir in "${TEMP_DIRS[@]}"; do
    rm -rf "$tmpdir" && echo "  ✓ Temp gelöscht: $tmpdir"
  done
  
  # Mount-Base löschen (falls leer)
  [[ -d "$MOUNT_BASE" ]] && rmdir "$MOUNT_BASE" 2>/dev/null || true
}

# Trap für Cleanup bei Abbruch
trap cleanup_mounts EXIT INT TERM

# === TARGET PREPARATION ===
if [[ $AUTO_MOUNT -eq 1 ]]; then
  mkdir -p "$MOUNT_BASE"
  
  for target in "${TARGETS[@]}"; do
    if [[ -f "$target" ]]; then
      # Image?
      if [[ "$target" =~ \.(img|iso|dd|bin|raw|dmg|vhd|vhdx|vmdk)$ ]]; then
        mount_image "$target"
      # Archiv?
      elif [[ "$target" =~ \.(zip|tar|tgz|tar\.gz|tar\.xz|txz|7z|rar)$ ]]; then
        extract_archive "$target"
      else
        REAL_TARGETS+=("$target")
      fi
    elif [[ -b "$target" ]]; then
      # Block Device
      mount_device "$target"
    else
      # Reguläres Verzeichnis
      REAL_TARGETS+=("$target")
    fi
  done
else
  REAL_TARGETS=("${TARGETS[@]}")
fi

# Prüfe ob wir Targets haben
if [[ ${#REAL_TARGETS[@]} -eq 0 ]]; then
  echo "ERROR: Keine gültigen Targets nach Auto-Mount" >&2
  exit 1
fi

echo ">>> Finale Targets: ${REAL_TARGETS[*]}"

# === HRM SCANNER AUSFÜHREN ===
# ... [Rest wie gehabt, aber mit REAL_TARGETS statt TARGETS] ...
```

---

## Zusammenfassung & Nächste Schritte

### ✅ Empfehlung: **HYBRID-ANSATZ**

1. **HRM Swarm Scanner** als Haupt-Engine
2. **Wrapper erweitern** mit Auto-Mount
3. **Legacy-Scanner** optional behalten (in `scripts/legacy/`)

### 🔧 Implementierung:

**JETZT:**
1. Erweitere `hrm_swarm_scanner_wrapper.sh` mit Auto-Mount
2. Teste mit Images & Archives
3. Dokumentiere

**SPÄTER (Optional):**
1. Migriere alte Scanner nach `scripts/legacy/`
2. Füge GUI-Option "Legacy-Scanner anzeigen" hinzu
3. Update Dokumentation

### 📝 Entscheidung benötigt:

**Soll ich:**
- ✅ **A) Auto-Mount im Wrapper implementieren** (empfohlen)
- ⏸️ **B) Alte Scanner behalten wie sie sind** (Status Quo)
- 🔄 **C) Komplett neuen Unified-Scanner erstellen**

**Ihre Entscheidung?**
