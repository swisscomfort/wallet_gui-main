#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$HOME/.local/share/wallet-gui/scripts/wallet_harvest_any.sh"

ROOT="${1:-}"
if [[ -z "$ROOT" ]]; then
  echo "ERROR: ROOT fehlt" >&2
  exit 2
fi
shift || true

# Wenn die GUI keine Targets übergibt: ROOT als Target verwenden
if [[ $# -eq 0 ]]; then
  echo "WARN: keine Targets übergeben – scanne ROOT ($ROOT)"
  set -- "$ROOT"
fi

exec "$SCRIPT" "$ROOT" "$@"
