#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

BUNDLE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$BUNDLE_DIR"

[[ -f SHA256SUMS && -f manifest.json && -f images.tar && -f models.tar.gz ]] || {
  echo "Offline bundle is incomplete" >&2
  exit 1
}
sha256sum --check --strict SHA256SUMS

PROJECT_NAME="hezqen-airgapped-rag"
OLLAMA_VOLUME="${PROJECT_NAME}_ollama_data"
QDRANT_STORAGE_VOLUME="${PROJECT_NAME}_qdrant_storage"
QDRANT_SNAPSHOT_VOLUME="${PROJECT_NAME}_qdrant_snapshots"
OLLAMA_IMAGE="$(python3 -c 'import json; print(json.load(open("manifest.json"))["images"]["ollama"])')"
QDRANT_IMAGE="$(python3 -c 'import json; print(json.load(open("manifest.json"))["images"]["qdrant"])')"

docker load -i images.tar
docker volume create "$OLLAMA_VOLUME" >/dev/null
docker volume create "$QDRANT_STORAGE_VOLUME" >/dev/null
docker volume create "$QDRANT_SNAPSHOT_VOLUME" >/dev/null

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/target" \
  --mount "type=bind,src=$BUNDLE_DIR/models.tar.gz,dst=/models.tar.gz,readonly" \
  --entrypoint /bin/bash "$OLLAMA_IMAGE" -lc \
  'tar -xzf /models.tar.gz -C /target && chown -R 10002:10002 /target'

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$QDRANT_STORAGE_VOLUME,dst=/qdrant/storage" \
  --mount "type=volume,src=$QDRANT_SNAPSHOT_VOLUME,dst=/qdrant/snapshots" \
  --entrypoint /bin/sh "$QDRANT_IMAGE" -c \
  'chown -R 1000:1000 /qdrant/storage /qdrant/snapshots'

if [[ ! -f .env ]]; then cp .env.example .env; chmod 600 .env; fi
export COMPOSE_PROJECT_NAME="$PROJECT_NAME"
docker compose up -d --pull never --wait --wait-timeout 180
echo "Offline RAG stack installed. API: http://127.0.0.1:8090"
