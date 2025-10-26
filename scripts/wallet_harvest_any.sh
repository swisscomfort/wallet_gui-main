#!/usr/bin/env bash
# Universeller Wallet-Scanner (Ordner, Images, Devices)
# Usage:
#   wallet_harvest_any.sh ROOT [--aggressive] [--exclude REGEX] [--stage] [--auto-mount] TARGET...
# Beispiele:
#   wallet_harvest_any.sh /run/media/emil/DATEN --aggressive --stage /run/media/emil/DATEN/Software/Collected
#   wallet_harvest_any.sh /run/media/emil/DATEN --auto-mount /run/media/emil/DATEN/hitachi_sdc3.img
#   wallet_harvest_any.sh /run/media/emil/DATEN /dev/sdb

set -Eeuo pipefail

ROOT="${1:-}"; shift || true
if [[ -z "${ROOT:-}" ]]; then
  echo "ERROR: ROOT fehlt"; exit 2
fi

AGGRESSIVE=0
STAGE=0
EXCLUDE_REGEX=""
AUTO_MOUNT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aggressive) AGGRESSIVE=1; shift;;
    --stage) STAGE=1; shift;;
    --exclude) EXCLUDE_REGEX="${2:-}"; shift 2;;
    --auto-mount) AUTO_MOUNT=1; shift;;
    *) break;;
  esac
done

if [[ $# -lt 1 ]]; then
  echo "ERROR: Mindestens ein TARGET angeben"; exit 2
fi

mkdir -p "${ROOT}/_logs" "${ROOT}/Software/_staging_wallets" "${ROOT}/_mount"
TS="$(date +%Y%m%d_%H%M%S)"
OUT="${ROOT}/_logs/walletscan_${TS}"
LOG="${OUT}/scan.log"
mkdir -p "${OUT}"
echo "OUT=${OUT}" | tee -a "$LOG"

CAND_NUL="${OUT}/candidates.nul"
> "$CAND_NUL"

MOUNT_BASE="${ROOT}/_mount/autoscan_${TS}"
MOUNTS=()  # mountpunkte
LOOPS=()   # loop devices

is_image_file() {
  local f="$1"
  [[ "$f" =~ \.(img|iso|dd|bin|raw|vhd|vhdx|vmdk|dmg)$ ]] && return 0 || return 1
}

add_candidates_from_dir() {
  local dir="$1"
  [[ -z "$dir" ]] && return 0
  if [[ -n "$EXCLUDE_REGEX" ]]; then
    find "$dir" -xdev -type f \
      \( -iname 'wallet.dat' -o -iname 'electrum*' -o -iname '*keystore*' -o -iname '*metamask*' -o \
         -iregex '.*\.\(txt\|json\|log\|ini\|conf\|cfg\|csv\|sqlite\|db\|db3\|ldb\|dat\|kdbx\|pem\|key\|der\|p12\|asc\)' \) \
      | grep -Ev "$EXCLUDE_REGEX" | tr '\n' '\0' >> "$CAND_NUL" || true
  else
    find "$dir" -xdev -type f \
      \( -iname 'wallet.dat' -o -iname 'electrum*' -o -iname '*keystore*' -o -iname '*metamask*' -o \
         -iregex '.*\.\(txt\|json\|log\|ini\|conf\|cfg\|csv\|sqlite\|db\|db3\|ldb\|dat\|kdbx\|pem\|key\|der\|p12\|asc\)' \) \
      -print0 >> "$CAND_NUL" 2>/dev/null || true
  fi
}

try_mount_image_or_device() {
  local target="$1"
  mkdir -p "$MOUNT_BASE"
  echo ">> mount-versuch: $target" | tee -a "$LOG"
  # losetup nur für Dateien
  local dev=""
  if [[ -f "$target" ]]; then
    dev="$(losetup --read-only --find --show -P "$target" || true)"
    if [[ -n "$dev" ]]; then
      LOOPS+=("$dev")
    fi
  elif [[ -b "$target" ]]; then
    dev="$target"
  fi
  if [[ -z "$dev" ]]; then
    echo "   (kein Device ermittelt)" | tee -a "$LOG"
    return 1
  fi
  # vorhandene Partitionen?
  local parts
  parts=$(lsblk -nrpo NAME,TYPE "$dev" | awk '$2=="part"{print $1}' || true)
  if [[ -z "$parts" ]]; then
    parts="$dev"
  fi
  local idx=0
  while read -r p; do
    [[ -z "$p" ]] && continue
    local mp="${MOUNT_BASE}/p${idx}"
    mkdir -p "$mp"
    if mount -o ro -t auto "$p" "$mp" 2>>"$LOG"; then
      echo "   gemountet: $p -> $mp" | tee -a "$LOG"
      MOUNTS+=("$mp")
      add_candidates_from_dir "$mp"
    else
      # spezifische Fallbacks
      if blkid -s TYPE -o value "$p" | grep -qi ntfs; then
        if mount -t ntfs3 -o ro "$p" "$mp" 2>>"$LOG" || ntfs-3g -o ro "$p" "$mp" 2>>"$LOG"; then
          echo "   gemountet (ntfs): $p -> $mp" | tee -a "$LOG"
          MOUNTS+=("$mp")
          add_candidates_from_dir "$mp"
        else
          rmdir "$mp" 2>/dev/null || true
        fi
      else
        rmdir "$mp" 2>/dev/null || true
      fi
    fi
    idx=$((idx+1))
  done <<< "$parts"
}

cleanup_mounts() {
  set +e
  for m in "${MOUNTS[@]}"; do
    umount "$m" 2>/dev/null || true
  done
  for l in "${LOOPS[@]}"; do
    losetup -d "$l" 2>/dev/null || true
  done
  set -e
}

# Targets sammeln (Ordner/Dateien/Devices)
TARGETS=("$@")

# Falls AUTO_MOUNT=1: Images/Devices read-only einhängen und mit scannen
if [[ "$AUTO_MOUNT" -eq 1 ]]; then
  for t in "${TARGETS[@]}"; do
    if [[ -f "$t" && "$(is_image_file "$t"; echo $?)" -eq 0 ]] || [[ -b "$t" ]]; then
      try_mount_image_or_device "$t" || true
    fi
  done
fi

# Ordner direkt scannen
for t in "${TARGETS[@]}"; do
  if [[ -d "$t" ]]; then
    add_candidates_from_dir "$t"
  fi
done

# Aggressive: auch ohne Kandidatenliste die Ziele durchsuchen
if [[ "$AGGRESSIVE" -eq 1 && ! -s "$CAND_NUL" ]]; then
  echo "AGGRESSIVE: gesamte Ziele inhaltsbasiert scannen" | tee -a "$LOG"
  for t in "${TARGETS[@]}"; do
    if [[ -d "$t" ]]; then
      find "$t" -xdev -type f -print0 >> "$CAND_NUL" 2>/dev/null || true
    fi
  done
fi

# Duplikate entfernen (optional)
if command -v sort >/dev/null 2>&1; then
  tr '\0' '\n' < "$CAND_NUL" | awk 'NF' | sort -u | tr '\n' '\0' > "${CAND_NUL}.dedup"
  mv "${CAND_NUL}.dedup" "$CAND_NUL"
fi

HITS="${OUT}/hits.txt"
HITS_TSV="${OUT}/hits.tsv"
MNEM="${OUT}/mnemonic_raw.txt"
touch "$HITS" "$MNEM"

# Inhaltssuche
if [[ -s "$CAND_NUL" ]]; then
  echo ">> Kandidaten: $(tr '\0' '\n' < "$CAND_NUL" | wc -l) Dateien" | tee -a "$LOG"
  xargs -0 -a "$CAND_NUL" \
    grep -aHnE 'wallet\.dat|electrum|metamask|keystore|bip(39|32)|mnemonic|seed( phrase)?|xpub|xprv|bc1[ac-hj-np-z02-9]{25,87}|0x[a-fA-F0-9]{40}' \
    > "$HITS" 2>/dev/null || true

  # TSV erzeugen: file \t line \t text
  awk -F: 'NF>=3{file=$1;line=$2;$1="";$2=""; sub(/^:/,""); txt=$0; gsub(/\t/," ",txt); print file "\t" line "\t" txt}' "$HITS" > "$HITS_TSV" || true

  # Mnemonic-Grobextraktion nur für Textdateien (schnell)
  xargs -0 -a "$CAND_NUL" -I{} sh -c '
    case "{}" in
      *.txt|*.log|*.json|*.ini|*.conf|*.cfg|*.csv)
        grep -aEo "([a-z]{3,8}[[:space:]]+){11,23}[a-z]{3,8}" "{}" || true
      ;;
    esac
  ' | tr -s "[:space:]" " " > "$MNEM" 2>/dev/null || true
else
  echo "WARN: Keine Kandidaten ermittelt." | tee -a "$LOG"
fi

# Optionales Staging (Symlinks) aus Hits
if [[ "$STAGE" -eq 1 && -s "$HITS" ]]; then
  STAGING="${ROOT}/Software/_staging_wallets"
  mkdir -p "$STAGING"
  cut -d$'\t' -f1 "$HITS_TSV" | sed 's/\t.*//' | while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    hash="$(printf "%s" "$f" | md5sum | awk '{print $1}')"
    link="${STAGING}/${base}__${hash:0:8}"
    [[ -e "$link" ]] || ln -s "$f" "$link" 2>/dev/null || true
  done
fi

# Summary
{
  echo "OUT=${OUT}"
  echo "ROOT=${ROOT}"
  echo "CANDIDATES=$(tr '\0' '\n' < "$CAND_NUL" | awk 'NF' | wc -l)"
  echo "HITS=$(wc -l < "$HITS")"
  echo "MNEMONIC_LINES=$(wc -l < "$MNEM")"
} | tee "${OUT}/summary.txt"

# Aufräumen
cleanup_mounts || true

echo "Fertig. Ergebnisse unter: ${OUT}"
