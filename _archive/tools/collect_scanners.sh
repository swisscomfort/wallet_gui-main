#!/usr/bin/env bash
set -Eeuo pipefail

DEST="$HOME/.local/share/wallet-gui/scripts"
LOG="$HOME/.local/share/wallet-gui/SCANNERS_FOUND.tsv"
mkdir -p "$DEST"

# Suchorte: gerne ergänzen
SEARCH_DEFAULT=("$HOME" "/run/media/emil/DATEN")
SEARCH=( "$@" )
[ ${#SEARCH[@]} -gt 0 ] || SEARCH=( "${SEARCH_DEFAULT[@]}" )

echo -e "alias\ttype\tkeywords\toriginal" >"$LOG"

count=0
# Kandidaten: ausführbare Dateien, .sh, .py – max. 5 MB (Header/Quelltext)
while IFS= read -r -d '' f; do
  mime="$(file -b "$f" 2>/dev/null || true)"
  case "$mime" in
    *script*|*text*executable*|*Python*script*)
      # Nur Scanner-nahe Dateien (Wallet/Seed/… inhaltlich)
      if grep -IaqE 'wallet|mnemonic|keystore|electrum|metamask|xpub|xprv|seed' "$f" 2>/dev/null; then
        base="$(basename "$f")"
        alias="$(echo "$base" | tr ' ' '_' | tr -cd 'A-Za-z0-9._-')"
        [[ "$alias" =~ \.sh$|\.py$ ]] || alias="${alias}.sh"   # GUI filtert *.sh – daher .sh suffix

        target="$DEST/$alias"
        i=1
        while [[ -e "$target" ]]; do
          target="$DEST/${alias%.*}_$i.${alias##*.}"
          ((i++))
        done

        # Wrapper erzeugen: ruft Original mit allen Parametern auf
        {
          echo '#!/usr/bin/env bash'
          echo 'set -Eeuo pipefail'
          echo "ORIG=$(printf %q \"$f\")"
          # Shebang/MIME entscheiden, womit wir starten
          if echo "$mime" | grep -qi python; then
            echo 'exec python3 "$ORIG" "$@"'
          else
            echo 'exec bash "$ORIG" "$@"'
          fi
        } >"$target"
        chmod +x "$target"

        keys="$(grep -IaoE 'wallet|mnemonic|keystore|electrum|metamask|xpub|xprv|seed' "$f" | tr '\n' ' ' | awk '{$1=$1};1' | head -c 120)"
        printf "%s\t%s\t%s\t%s\n" "$(basename "$target")" "$mime" "$keys" "$f" >> "$LOG"
        ((count++))
      fi
    ;;
  esac
done < <(find "${SEARCH[@]}" -xdev -type f \( -name '*.sh' -o -name '*.py' -o -perm -111 \) -size -5M -print0 2>/dev/null)

echo "Fertig: $count Scanner verlinkt / verpackt → $DEST"
echo "Liste:  $LOG"
