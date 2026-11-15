#!/usr/bin/env bash
set -Eeuo pipefail

OLLAMA_IMAGE="${OLLAMA_IMAGE:-hezqen/ollama:0.40.16-nonroot}"
OLLAMA_VOLUME="${OLLAMA_VOLUME:-hezqen-airgapped-rag_ollama_data}"
CONTAINER="hezqen-ollama-model-prep-$$"
MODELS="${HEZQEN_MODELS:-nomic-embed-text qwen2.5:0.5b}"

docker image inspect "$OLLAMA_IMAGE" >/dev/null
docker volume create "$OLLAMA_VOLUME" >/dev/null
docker run -d --rm --name "$CONTAINER" --network bridge --user 10002:10002 \
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/home/ollama/.ollama" \
  "$OLLAMA_IMAGE" >/dev/null
cleanup() { docker rm -f "$CONTAINER" >/dev/null 2>&1 || true; }
trap cleanup EXIT

for attempt in $(seq 1 60); do
  if docker exec "$CONTAINER" ollama ps >/dev/null 2>&1; then break; fi
  sleep 2
done
docker exec "$CONTAINER" ollama ps >/dev/null

for model in $MODELS; do
  echo "Preparing model artifact: $model"
  docker exec "$CONTAINER" ollama pull "$model"
done

docker exec "$CONTAINER" ollama list
echo "Model volume prepared. Export it with scripts/package-offline.sh before moving to the offline host."
