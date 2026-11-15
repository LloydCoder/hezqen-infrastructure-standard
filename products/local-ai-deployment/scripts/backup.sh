#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

PRODUCT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$PRODUCT_DIR"

usage() {
  echo "Usage: $0 BACKUP_DIRECTORY" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
BACKUP_DIR="$1"
mkdir -p -- "$BACKUP_DIR"
BACKUP_DIR="$(cd -- "$BACKUP_DIR" && pwd -P)"
[[ "$BACKUP_DIR" != *","* && "$BACKUP_DIR" != *$'\n'* ]] || { echo "Backup path cannot contain commas or newlines" >&2; exit 2; }
chmod 700 "$BACKUP_DIR"
[[ -z "$(find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]] || {
  echo "Backup directory must be empty" >&2
  exit 1
}

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
  docker volume inspect "$volume" >/dev/null
done
docker image inspect "$HELPER_IMAGE" >/dev/null 2>&1 || {
  echo "Backup helper image not found: $HELPER_IMAGE. Build the product images first." >&2
  exit 1
}
docker run --rm --network none --entrypoint /bin/sh "$HELPER_IMAGE" -euc 'command -v tar >/dev/null && tar --version >/dev/null'

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
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/source,readonly" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'tar --numeric-owner -czf - -C /source .' > "$BACKUP_DIR/ollama_data.tar.gz"

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$WEBUI_VOLUME,dst=/source,readonly" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'tar --numeric-owner -czf - -C /source .' > "$BACKUP_DIR/open_webui_data.tar.gz"

(
  cd "$BACKUP_DIR"
  sha256sum ollama_data.tar.gz > ollama_data.tar.gz.sha256
  sha256sum open_webui_data.tar.gz > open_webui_data.tar.gz.sha256
)

python3 - "$BACKUP_DIR" "$PROJECT_NAME" "$OLLAMA_VOLUME" "$WEBUI_VOLUME" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

directory, project, ollama_volume, webui_volume = sys.argv[1:]
product = json.loads((Path.cwd() / "product-manifest.json").read_text(encoding="utf-8"))
manifest = {
    "schemaVersion": "1.0.0",
    "product": product["id"],
    "productVersion": product["version"],
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "composeProject": project,
    "volumes": {
        "ollama": ollama_volume,
        "openWebUI": webui_volume,
    },
    "archives": {
        "ollama": "ollama_data.tar.gz",
        "openWebUI": "open_webui_data.tar.gz",
    },
}
(Path(directory) / "backup-manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
PY

echo "Backup created at: $BACKUP_DIR"
