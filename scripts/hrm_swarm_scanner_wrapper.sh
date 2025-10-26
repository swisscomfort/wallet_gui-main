#!/usr/bin/env bash
# hrm_swarm_scanner_wrapper.sh v2.0 - GUI-kompatibles Wrapper-Skript für hrm_swarm_scanner.py
# Übersetzt GUI-Parameter in hrm_swarm_scanner Parameter
# NEU: Auto-Mount für Images, Archives und Devices

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCANNER="$SCRIPT_DIR/../standalone/hrm_swarm_scanner.py"

# GUI-Parameter parsen
ROOT="${1:-}"; shift || true
if [[ -z "${ROOT:-}" ]]; then
  echo "ERROR: ROOT fehlt"; exit 2
fi

AGGRESSIVE=0
STAGING=0
AUTO_MOUNT=0
EXCLUDE_REGEX=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aggressive) AGGRESSIVE=1; shift;;
    --staging) STAGING=1; shift;;
    --auto-mount) AUTO_MOUNT=1; shift;;
    --exclude) EXCLUDE_REGEX="${2:-}"; shift 2;;
    *) break;;
  esac
done

if [[ $# -lt 1 ]]; then
  echo "ERROR: Mindestens ein TARGET angeben"; exit 2
fi

TARGETS=("$@")

# === AUTO-MOUNT INFRASTRUCTURE ===
REAL_TARGETS=()
MOUNTS=()
LOOPS=()
TEMP_DIRS=()
MOUNT_BASE="${ROOT}/_mount/hrm_scan_$$"

# Cleanup-Funktion
cleanup_mounts() {
  local exit_code=$?
  
  if [[ ${#MOUNTS[@]} -gt 0 ]] || [[ ${#LOOPS[@]} -gt 0 ]] || [[ ${#TEMP_DIRS[@]} -gt 0 ]]; then
    echo ">>> Cleanup wird durchgeführt..."
  fi
  
  # Unmount all
  for mp in "${MOUNTS[@]}"; do
    if mountpoint -q "$mp" 2>/dev/null; then
      sudo umount "$mp" 2>/dev/null && echo "  ✓ Unmount: $mp" || echo "  ⚠ Unmount fehlgeschlagen: $mp"
    fi
    rmdir "$mp" 2>/dev/null || true
  done
  
  # Loop devices freigeben
  for loop in "${LOOPS[@]}"; do
    if [[ -e "$loop" ]]; then
      sudo losetup -d "$loop" 2>/dev/null && echo "  ✓ Loop freigegeben: $loop" || echo "  ⚠ Loop freigabe fehlgeschlagen: $loop"
    fi
  done
  
  # Temp-Verzeichnisse löschen
  for tmpdir in "${TEMP_DIRS[@]}"; do
    if [[ -d "$tmpdir" ]]; then
      rm -rf "$tmpdir" && echo "  ✓ Temp gelöscht: $tmpdir"
    fi
  done
  
  # Mount-Base löschen (falls leer)
  [[ -d "$MOUNT_BASE" ]] && rmdir "$MOUNT_BASE" 2>/dev/null || true
  
  exit $exit_code
}

# Trap für Cleanup bei Abbruch oder Exit
trap cleanup_mounts EXIT INT TERM

mount_image() {
  local img="$1"
  echo "  → Auto-Mount Image: $(basename "$img")"
  
  # Prüfe ob Datei existiert und lesbar ist
  if [[ ! -r "$img" ]]; then
    echo "    ✗ Datei nicht lesbar: $img"
    return 1
  fi
  
  # Loop device erstellen
  local dev=$(sudo losetup --read-only --find --show -P "$img" 2>/dev/null || true)
  if [[ -z "$dev" ]]; then
    echo "    ✗ Konnte Loop-Device nicht erstellen"
    return 1
  fi
  LOOPS+=("$dev")
  echo "    ✓ Loop-Device: $dev"
  
  # Kurz warten damit Partitionen erkannt werden
  sleep 0.5
  
  # Partitionen finden
  local parts=$(lsblk -nrpo NAME,TYPE "$dev" 2>/dev/null | awk '$2=="part"{print $1}')
  if [[ -z "$parts" ]]; then
    parts="$dev"  # Keine Partitionen, Device selbst mounten
  fi
  
  # Jede Partition mounten
  local idx=0
  local mounted=0
  while read -r part; do
    [[ -z "$part" ]] && continue
    local mp="$MOUNT_BASE/$(basename "$img" | sed 's/[^a-zA-Z0-9_-]/_/g')_p${idx}"
    mkdir -p "$mp"
    
    if sudo mount -o ro "$part" "$mp" 2>/dev/null; then
      echo "    ✓ Gemountet: $(basename "$part") → $mp"
      REAL_TARGETS+=("$mp")
      MOUNTS+=("$mp")
      ((mounted++))
    else
      echo "    ⚠ Konnte $(basename "$part") nicht mounten (evtl. unbekanntes Dateisystem)"
      rmdir "$mp" 2>/dev/null || true
    fi
    ((idx++))
  done <<< "$parts"
  
  if [[ $mounted -eq 0 ]]; then
    echo "    ✗ Keine Partition gemountet"
    return 1
  fi
  
  return 0
}

extract_archive() {
  local arch="$1"
  echo "  → Auto-Extract Archive: $(basename "$arch")"
  
  # Prüfe ob Datei existiert und lesbar ist
  if [[ ! -r "$arch" ]]; then
    echo "    ✗ Datei nicht lesbar: $arch"
    return 1
  fi
  
  local tmpdir=$(mktemp -d -p "$MOUNT_BASE" "hrm_extract_$(basename "$arch" | sed 's/[^a-zA-Z0-9_-]/_/g')_XXXXXX")
  TEMP_DIRS+=("$tmpdir")
  
  # Versuche verschiedene Entpacker
  local extracted=0
  
  # 7z (bevorzugt, unterstützt die meisten Formate)
  if command -v 7z &>/dev/null; then
    if 7z x -y -o"$tmpdir" "$arch" &>/dev/null; then
      echo "    ✓ Entpackt mit 7z"
      extracted=1
    fi
  fi
  
  # unzip für ZIP
  if [[ $extracted -eq 0 ]] && [[ "$arch" =~ \.(zip|ZIP)$ ]] && command -v unzip &>/dev/null; then
    if unzip -q "$arch" -d "$tmpdir" 2>/dev/null; then
      echo "    ✓ Entpackt mit unzip"
      extracted=1
    fi
  fi
  
  # tar für TAR, TGZ, TAR.GZ, TAR.XZ
  if [[ $extracted -eq 0 ]] && [[ "$arch" =~ \.(tar|tgz|tar\.gz|tar\.xz|txz|tar\.bz2)$ ]] && command -v tar &>/dev/null; then
    if tar -xf "$arch" -C "$tmpdir" 2>/dev/null; then
      echo "    ✓ Entpackt mit tar"
      extracted=1
    fi
  fi
  
  if [[ $extracted -eq 1 ]]; then
    # Prüfe ob Inhalt vorhanden
    if [[ -n "$(ls -A "$tmpdir" 2>/dev/null)" ]]; then
      REAL_TARGETS+=("$tmpdir")
      return 0
    else
      echo "    ⚠ Archiv leer"
      return 1
    fi
  else
    echo "    ✗ Konnte Archiv nicht entpacken (7z/unzip/tar benötigt)"
    return 1
  fi
}

mount_device() {
  local dev="$1"
  echo "  → Auto-Mount Device: $dev"
  
  # Prüfe ob Device existiert
  if [[ ! -b "$dev" ]]; then
    echo "    ✗ Kein Block-Device: $dev"
    return 1
  fi
  
  # Partitionen prüfen
  local parts=$(lsblk -nrpo NAME,TYPE "$dev" 2>/dev/null | awk '$2=="part"{print $1}')
  if [[ -z "$parts" ]]; then
    parts="$dev"  # Keine Partitionen, Device selbst
  fi
  
  local idx=0
  local mounted=0
  while read -r part; do
    [[ -z "$part" ]] && continue
    local mp="$MOUNT_BASE/$(basename "$dev")_p${idx}"
    mkdir -p "$mp"
    
    if sudo mount -o ro "$part" "$mp" 2>/dev/null; then
      echo "    ✓ Gemountet: $(basename "$part") → $mp"
      REAL_TARGETS+=("$mp")
      MOUNTS+=("$mp")
      ((mounted++))
    else
      echo "    ⚠ Konnte $(basename "$part") nicht mounten"
      rmdir "$mp" 2>/dev/null || true
    fi
    ((idx++))
  done <<< "$parts"
  
  if [[ $mounted -eq 0 ]]; then
    echo "    ✗ Keine Partition gemountet"
    return 1
  fi
  
  return 0
}

# === TARGET PREPARATION ===
if [[ $AUTO_MOUNT -eq 1 ]]; then
  echo ">>> Auto-Mount aktiviert, verarbeite Targets..."
  mkdir -p "$MOUNT_BASE"
  
  for target in "${TARGETS[@]}"; do
    if [[ -f "$target" ]]; then
      # Image-Datei?
      if [[ "$target" =~ \.(img|iso|dd|bin|raw|dmg|vhd|vhdx|vmdk|IMG|ISO|DD|BIN|RAW|DMG|VHD|VHDX|VMDK)$ ]]; then
        mount_image "$target" || echo "  ⚠ Überspringe: $target"
      
      # Archiv?
      elif [[ "$target" =~ \.(zip|tar|tgz|tar\.gz|tar\.xz|txz|tar\.bz2|7z|rar|ZIP|TAR|TGZ|7Z|RAR)$ ]]; then
        extract_archive "$target" || echo "  ⚠ Überspringe: $target"
      
      # Reguläre Datei
      else
        echo "  → Reguläre Datei: $target"
        REAL_TARGETS+=("$target")
      fi
    
    elif [[ -b "$target" ]]; then
      # Block Device
      mount_device "$target" || echo "  ⚠ Überspringe: $target"
    
    elif [[ -d "$target" ]]; then
      # Reguläres Verzeichnis
      echo "  → Verzeichnis: $target"
      REAL_TARGETS+=("$target")
    
    else
      echo "  ✗ Nicht gefunden: $target"
    fi
  done
else
  # Kein Auto-Mount, Targets direkt übernehmen
  REAL_TARGETS=("${TARGETS[@]}")
fi

# Prüfe ob wir Targets haben
if [[ ${#REAL_TARGETS[@]} -eq 0 ]]; then
  echo "ERROR: Keine gültigen Targets nach Verarbeitung" >&2
  exit 1
fi

echo ">>> Finale Targets: ${#REAL_TARGETS[@]} Verzeichnis(se)"
for rt in "${REAL_TARGETS[@]}"; do
  echo "    - $rt"
done

# === SCANNER EXECUTION ===
# Erstelle Output-Verzeichnis im GUI-Format
TS="$(date +%Y%m%d_%H%M%S)"
OUT="${ROOT}/_logs/walletscan_${TS}"
mkdir -p "${OUT}"
echo "OUT=${OUT}"

# Scanner-Parameter aufbauen
SCANNER_ARGS=()
SCANNER_ARGS+=(--root "$ROOT")

# Targets hinzufügen (die vorbereiteten REAL_TARGETS)
for t in "${REAL_TARGETS[@]}"; do
  SCANNER_ARGS+=(--target "$t")
done

# Threads basierend auf Aggressivität
if [[ $AGGRESSIVE -eq 1 ]]; then
  SCANNER_ARGS+=(--threads 10)
  SCANNER_ARGS+=(--max-mb 1024)
else
  SCANNER_ARGS+=(--threads 6)
  SCANNER_ARGS+=(--max-mb 512)
fi

# Exclude-Pattern
if [[ -n "$EXCLUDE_REGEX" ]]; then
  SCANNER_ARGS+=(--exclude "$EXCLUDE_REGEX")
fi

# YARA bei aggressiv aktivieren
if [[ $AGGRESSIVE -eq 1 ]]; then
  SCANNER_ARGS+=(--yara)
fi

# Prefer ripgrep
SCANNER_ARGS+=(--prefer-rg)

# Scanner ausführen
echo ">>> HRM Swarm Scanner wird gestartet..."
echo ">>> Parameter: ${SCANNER_ARGS[*]}"

# Führe Scanner aus und speichere Output
SCANNER_OUTPUT_FILE="${OUT}/scanner_output.log"
python3 "$SCANNER" "${SCANNER_ARGS[@]}" 2>&1 | tee "$SCANNER_OUTPUT_FILE"

# Extrahiere Scanner-Output-Verzeichnis aus der Ausgabe
SCANNER_OUT=$(grep -oP '"out":\s*"\K[^"]+' "$SCANNER_OUTPUT_FILE" 2>/dev/null | tail -1 || echo "")

# Fallback: Suche das neueste hrm_swarm_* Verzeichnis
if [[ -z "$SCANNER_OUT" ]] || [[ ! -d "$SCANNER_OUT" ]]; then
  echo ">>> Suche Scanner-Output-Verzeichnis..."
  SCANNER_OUT=$(find "${ROOT}/_logs" -maxdepth 1 -type d -name "hrm_swarm_*" 2>/dev/null | sort | tail -1)
fi

if [[ -n "$SCANNER_OUT" ]] && [[ -d "$SCANNER_OUT" ]]; then
  echo ">>> Konvertiere Ergebnisse ins GUI-Format..."
  echo ">>> Scanner-Output gefunden: $SCANNER_OUT"
  
  # Konvertiere hits.json zu hits.txt
  if [[ -f "${SCANNER_OUT}/hits.json" ]]; then
    python3 -c "
import json, sys
with open('${SCANNER_OUT}/hits.json', 'r') as f:
    hits = json.load(f)
with open('${OUT}/hits.txt', 'w') as out:
    for hit in hits:
        file = hit.get('file', '')
        line = hit.get('line', 0)
        snippet = hit.get('snippet', '').replace('\n', ' ').strip()
        out.write(f\"{file}:{line}:{snippet}\n\")
" 2>/dev/null || true
    echo "✓ hits.txt erstellt ($(wc -l < "${OUT}/hits.txt") Treffer)"
  fi
  
  # Konvertiere mnemonics.json zu mnemonic_raw.txt
  if [[ -f "${SCANNER_OUT}/mnemonics.json" ]]; then
    python3 -c "
import json, sys
with open('${SCANNER_OUT}/mnemonics.json', 'r') as f:
    mnems = json.load(f)
with open('${OUT}/mnemonic_raw.txt', 'w') as out:
    for m in mnems:
        file = m.get('file', '')
        line = m.get('line', 0)
        mnemonic = m.get('mnemonic', '')
        out.write(f\"# {file}:{line}\n{mnemonic}\n\n\")
" 2>/dev/null || true
    echo "✓ mnemonic_raw.txt erstellt ($(grep -c '^# ' "${OUT}/mnemonic_raw.txt") Kandidaten)"
  fi
  
  # Kopiere summary.json
  if [[ -f "${SCANNER_OUT}/summary.json" ]]; then
    cp "${SCANNER_OUT}/summary.json" "${OUT}/summary.json"
    echo "✓ summary.json kopiert"
  fi
  
  # Erstelle scan.log
  cat > "${OUT}/scan.log" << EOF
=== HRM Swarm Scanner ===
Started: $(date)
ROOT: $ROOT
TARGETS: ${TARGETS[*]}
AGGRESSIVE: $AGGRESSIVE
OUTPUT: $OUT
SCANNER_OUTPUT: $SCANNER_OUT

Summary:
$(cat "${SCANNER_OUT}/summary.json" 2>/dev/null || echo "{}")

Completed: $(date)
EOF
  
  echo "✓ scan.log erstellt"
  
  # Staging (Symlinks) wenn gewünscht
  if [[ $STAGING -eq 1 ]]; then
    echo ">>> Erstelle Staging-Symlinks..."
    STAGE_DIR="${ROOT}/Software/_staging_wallets/${TS}"
    mkdir -p "$STAGE_DIR"
    
    if [[ -f "${OUT}/hits.txt" ]]; then
      while IFS=: read -r file rest; do
        [[ -z "$file" ]] && continue
        [[ ! -f "$file" ]] && continue
        
        # Erstelle Symlink mit relativem Pfad
        base=$(basename "$file")
        target="$STAGE_DIR/$base"
        
        # Bei Duplikaten: nummerieren
        if [[ -e "$target" ]]; then
          i=1
          while [[ -e "${target}.${i}" ]]; do
            ((i++))
          done
          target="${target}.${i}"
        fi
        
        ln -sf "$file" "$target" 2>/dev/null || true
      done < <(cut -d: -f1 "${OUT}/hits.txt" | sort -u)
      
      echo "✓ Staging-Symlinks erstellt: $STAGE_DIR"
    fi
  fi
  
else
  echo "ERROR: Scanner-Output nicht gefunden: $SCANNER_OUT" >&2
  exit 1
fi

echo ">>> HRM Swarm Scanner abgeschlossen!"
echo ">>> Ergebnisse: $OUT"
