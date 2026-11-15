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
python3 -c 'import json; m=json.load(open("manifest.json", encoding="utf-8")); assert m.get("product") == "airgapped-rag" and m.get("productVersion") == "0.1.0", "offline bundle identity/version mismatch"'

PROJECT_NAME="hezqen-airgapped-rag"
OLLAMA_VOLUME="${PROJECT_NAME}_ollama_data"
QDRANT_STORAGE_VOLUME="${PROJECT_NAME}_qdrant_storage"
QDRANT_SNAPSHOT_VOLUME="${PROJECT_NAME}_qdrant_snapshots"
OLLAMA_IMAGE="$(python3 -c 'import json; print(json.load(open("manifest.json"))["images"]["ollama"])')"
QDRANT_IMAGE="$(python3 -c 'import json; print(json.load(open("manifest.json"))["images"]["qdrant"])')"
RAG_API_IMAGE="$(python3 -c 'import json; print(json.load(open("manifest.json"))["images"]["ragApi"])')"
RAG_EMBED_MODEL="$(python3 -c 'import json; print(json.load(open("manifest.json"))["embeddingModel"])')"
RAG_CHAT_MODEL="$(python3 -c 'import json; print(json.load(open("manifest.json"))["chatModel"])')"
export OLLAMA_IMAGE QDRANT_IMAGE RAG_API_IMAGE RAG_EMBED_MODEL RAG_CHAT_MODEL

python3 -c 'import json; m=json.load(open("manifest.json")); l=json.load(open("images.lock.json")); assert m["images"]["qdrant"].split("@")[-1] == l["images"]["qdrant"]["digest"], "Qdrant image lock mismatch"'
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
docker compose config --quiet
docker image inspect "$OLLAMA_IMAGE" "$QDRANT_IMAGE" "$RAG_API_IMAGE" >/dev/null
docker compose up -d --pull never --wait --wait-timeout 180
MODELS="$(docker compose exec -T ollama ollama list)"
while IFS= read -r model; do
  [[ -n "$model" ]] || continue
  grep -F "$model" <<<"$MODELS" >/dev/null || { echo "Required offline model missing: $model" >&2; exit 1; }
done < <(python3 -c 'import json; print("\n".join(json.load(open("manifest.json"))["models"]))')
echo "Offline RAG stack installed. API: http://127.0.0.1:8090"
