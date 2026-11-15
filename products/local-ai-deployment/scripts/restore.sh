#!/usr/bin/env bash
set -Eeuo pipefail

PRODUCT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$PRODUCT_DIR"

usage() {
  echo "Usage: $0 BACKUP_DIRECTORY --confirm" >&2
  exit 2
}

[[ $# -eq 2 && "$2" == "--confirm" ]] || usage
BACKUP_DIR="$(cd -- "$1" 2>/dev/null && pwd -P)" || { echo "Backup directory does not exist" >&2; exit 1; }
[[ "$BACKUP_DIR" != *","* && "$BACKUP_DIR" != *$'\n'* ]] || { echo "Backup path cannot contain commas or newlines" >&2; exit 2; }

HELPER_IMAGE="${BACKUP_HELPER_IMAGE:-hezqen/ollama:0.40.16-nonroot}"
if [[ -n "${OLLAMA_VOLUME:-}" || -n "${WEBUI_VOLUME:-}" ]]; then
  [[ -n "${OLLAMA_VOLUME:-}" && -n "${WEBUI_VOLUME:-}" ]] || { echo "Set both OLLAMA_VOLUME and WEBUI_VOLUME, or neither" >&2; exit 2; }
  MANAGE_COMPOSE=false
else
  MANAGE_COMPOSE=true
fi

PROJECT_NAME="$(docker compose config --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["name"])')"
OLLAMA_VOLUME="${OLLAMA_VOLUME:-${PROJECT_NAME}_ollama_data}"
WEBUI_VOLUME="${WEBUI_VOLUME:-${PROJECT_NAME}_open_webui_data}"

for volume in "$OLLAMA_VOLUME" "$WEBUI_VOLUME"; do
  [[ "$volume" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]] || { echo "Invalid Docker volume name: $volume" >&2; exit 2; }
done
docker image inspect "$HELPER_IMAGE" >/dev/null 2>&1 || {
  echo "Backup helper image not found: $HELPER_IMAGE. Build the product images first." >&2
  exit 1
}

[[ -f "$BACKUP_DIR/backup-manifest.json" ]] || { echo "backup-manifest.json is missing" >&2; exit 1; }
python3 - "$BACKUP_DIR/backup-manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if manifest.get("schemaVersion") != "1.0.0":
    raise SystemExit("Unsupported backup manifest schema")
expected = {
    "ollama": "ollama_data.tar.gz",
    "openWebUI": "open_webui_data.tar.gz",
}
if manifest.get("archives") != expected:
    raise SystemExit("Backup manifest archive map is invalid")
PY

(
  cd "$BACKUP_DIR"
  sha256sum -c ollama_data.tar.gz.sha256
  sha256sum -c open_webui_data.tar.gz.sha256
)

docker run --rm --network none \
  --mount "type=bind,src=$BACKUP_DIR,dst=/backup,readonly" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc '
for archive in /backup/ollama_data.tar.gz /backup/open_webui_data.tar.gz; do
  if tar -tzf "$archive" | grep -Eq "(^/|(^|/)\.\.(/|$))"; then
    echo "Unsafe path found in archive: $archive" >&2
    exit 1
  fi
done
'

docker volume inspect "$OLLAMA_VOLUME" >/dev/null 2>&1 || docker volume create "$OLLAMA_VOLUME" >/dev/null
docker volume inspect "$WEBUI_VOLUME" >/dev/null 2>&1 || docker volume create "$WEBUI_VOLUME" >/dev/null

WAS_RUNNING=false
if [[ "$MANAGE_COMPOSE" == true ]] && [[ -n "$(docker compose ps --status running -q)" ]]; then
  WAS_RUNNING=true
  docker compose down
fi

restart_stack() {
  local status=$?
  trap - EXIT
  if [[ "$WAS_RUNNING" == true ]]; then
    docker compose up -d || status=1
  fi
  exit "$status"
}
trap restart_stack EXIT

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/target" \
  --mount "type=bind,src=$BACKUP_DIR,dst=/backup,readonly" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar --numeric-owner -xzf /backup/ollama_data.tar.gz -C /target'

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$WEBUI_VOLUME,dst=/target" \
  --mount "type=bind,src=$BACKUP_DIR,dst=/backup,readonly" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; tar --numeric-owner -xzf /backup/open_webui_data.tar.gz -C /target'

echo "Restore completed for volumes: $OLLAMA_VOLUME and $WEBUI_VOLUME"
