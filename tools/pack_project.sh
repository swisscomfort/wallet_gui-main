#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Pack a project into a single self-extracting .run bundle

set -euo pipefail

PROJECT_PATH="${1:-.}"
OUTPUT_FILE="${2:-}"
TEMP_DIR=""
WORK_DIR="$(pwd)"

# Logging
log_info() { echo "[INFO] $*" >&2; }
log_warn() { echo "[WARN] $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }
log_ok() { echo "[OK] $*" >&2; }

# Cleanup
cleanup() {
  [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]] && rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Validate
if [[ ! -d "$PROJECT_PATH" ]]; then
  log_error "Project not found: $PROJECT_PATH"
  exit 1
fi

log_ok "Project directory: $PROJECT_PATH"

# Check tools
for tool in bash tar gzip sha256sum python3; do
  if ! command -v "$tool" &>/dev/null; then
    log_error "Required tool missing: $tool"
    exit 1
  fi
done
log_ok "All required tools available"

# Setup
TEMP_DIR=$(mktemp -d)
PAYLOAD_DIR="$TEMP_DIR/payload"
mkdir -p "$PAYLOAD_DIR"

log_info "Workspace: $TEMP_DIR"

# Copy project files (with excludes)
log_info "Packaging project files..."
tar \
  --exclude=.git \
  --exclude=.venv \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude='*.pyc' \
  --exclude=build \
  --exclude=dist \
  --exclude=.DS_Store \
  --exclude='*.egg-info' \
  --exclude=node_modules \
  -czf "$PAYLOAD_DIR/project.tar.gz" \
  -C "$PROJECT_PATH" \
  . 2>/dev/null || {
  log_warn "Some files may have been skipped (this is normal)"
}
log_ok "Project packaged"

# Create pack report
{
  echo "=== Pack Report ==="
  echo "Date: $(date)"
  echo "Project: $PROJECT_PATH"
  echo "Timestamp: $(date +%s)"
} > "$PAYLOAD_DIR/pack_report.txt"

# Create payload archive
cd "$TEMP_DIR"
log_info "Creating payload..."
tar -czf payload.tar.gz payload/ 2>/dev/null
PAYLOAD_SHA=$(sha256sum payload.tar.gz | awk '{print $1}')
PAYLOAD_SIZE=$(stat -c%s payload.tar.gz 2>/dev/null || stat -f%z payload.tar.gz 2>/dev/null || echo "0")
log_ok "Payload ready: $PAYLOAD_SIZE bytes, SHA256: $PAYLOAD_SHA"

# Determine output filename
if [[ -z "$OUTPUT_FILE" ]]; then
  if [[ "$PROJECT_PATH" == "." ]]; then
    PROJECT_NAME=$(basename "$WORK_DIR" | sed 's/[^a-zA-Z0-9_-]/-/g')
  else
    PROJECT_NAME=$(basename "$PROJECT_PATH" | sed 's/[^a-zA-Z0-9_-]/-/g')
  fi
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  OUTPUT_FILE="${PROJECT_NAME}-bundle-${TIMESTAMP}.run"
fi

# Switch back to work directory
cd "$WORK_DIR"

# Create header file
HEADER_FILE="$TEMP_DIR/header.sh"
cat > "$HEADER_FILE" << 'HEADER_EOF'
#!/usr/bin/env bash
# Self-extracting bundle
# Usage: chmod +x bundle.run && ./bundle.run

set -euo pipefail

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
EXTRACT_DIR="${TMPDIR:-/tmp}/bundle_$$"

cleanup() { [[ -d "$EXTRACT_DIR" ]] && rm -rf "$EXTRACT_DIR"; }
trap cleanup EXIT

# Extract payload
mkdir -p "$EXTRACT_DIR"
HEADER_SIZE=$(grep -a -n "^__PAYLOAD_START__$" "$SELF" | cut -d: -f1)
PAYLOAD_OFFSET=$((HEADER_SIZE + 1))

echo "[INFO] Extracting bundle to $EXTRACT_DIR..."
tail -n +$PAYLOAD_OFFSET "$SELF" | tar -xzf - -C "$EXTRACT_DIR" || {
  echo "[ERROR] Failed to extract"
  exit 1
}

# Verify integrity
echo "[INFO] Verifying integrity..."
EXPECTED_SHA="PAYLOAD_SHA_PLACEHOLDER"
cd "$EXTRACT_DIR"
ACTUAL_SHA=$(tar -czf - payload/ 2>/dev/null | sha256sum | awk '{print $1}')

if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  echo "[ERROR] Integrity check failed!"
  exit 1
fi

echo "[OK] Bundle verified"
cd payload

# Auto-start logic
echo "[INFO] Starting application..."

# 1. Dockerfile
if [[ -f "project.tar.gz" ]] && tar -tzf project.tar.gz 2>/dev/null | grep -q "^Dockerfile$"; then
  tar -xzf project.tar.gz
  if command -v docker &>/dev/null; then
    echo "[INFO] Building and running Docker image..."
    PROJECT_NAME=$(basename "$PWD" | sed 's/[^a-zA-Z0-9_-]/-/g')
    docker build -t "$PROJECT_NAME:bundle" . >/dev/null 2>&1
    docker run --rm -v "$PWD":/workspace -w /workspace "$PROJECT_NAME:bundle"
    exit 0
  fi
fi

# 2. run.sh
if tar -tzf project.tar.gz 2>/dev/null | grep -q "^run\.sh$"; then
  tar -xzf project.tar.gz
  chmod +x run.sh 2>/dev/null || true
  ./run.sh
  exit 0
fi

# 3. Python
if tar -tzf project.tar.gz 2>/dev/null | grep -qE "(main\.py|app\.py)"; then
  echo "[INFO] Found Python project"
  tar -xzf project.tar.gz
  if [[ -f requirements.txt ]]; then
    echo "[INFO] Installing dependencies..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || true
  fi
  if [[ -f main.py ]]; then
    python3 -u main.py
  elif [[ -f app.py ]]; then
    python3 -u app.py
  fi
  exit 0
fi

# 4. Node.js
if tar -tzf project.tar.gz 2>/dev/null | grep -q "^package\.json$"; then
  echo "[INFO] Found Node.js project"
  tar -xzf project.tar.gz
  npm install --quiet 2>/dev/null || true
  npm start 2>/dev/null || echo "[ERROR] No start script found"
  exit 0
fi

echo "[ERROR] No recognized entrypoint found"
echo "[INFO] Available files:"
tar -tzf project.tar.gz | head -20
exit 1

__PAYLOAD_START__
HEADER_EOF

log_info "Creating self-extracting bundle..."

# Build the final bundle
cp "$HEADER_FILE" "$OUTPUT_FILE"
sed -i "s/PAYLOAD_SHA_PLACEHOLDER/$PAYLOAD_SHA/" "$OUTPUT_FILE"
cat "$TEMP_DIR/payload.tar.gz" >> "$OUTPUT_FILE"
chmod +x "$OUTPUT_FILE"

log_ok "Bundle created: $OUTPUT_FILE"
log_ok "Size: $PAYLOAD_SIZE bytes"
log_ok "SHA256: $PAYLOAD_SHA"
echo ""
echo "=== Summary ==="
echo "Output:   $OUTPUT_FILE"
echo "Project:  $PROJECT_PATH"
echo "Usage:    chmod +x $OUTPUT_FILE && ./$OUTPUT_FILE"
