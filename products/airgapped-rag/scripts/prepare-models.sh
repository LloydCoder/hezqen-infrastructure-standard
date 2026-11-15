#!/usr/bin/env bash
set -Eeuo pipefail
PRODUCT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
OLLAMA_IMAGE="${OLLAMA_IMAGE:-hezqen/ollama:0.40.16-nonroot}"
OLLAMA_VOLUME="${OLLAMA_VOLUME:-hezqen-airgapped-rag_ollama_data}"
CONTAINER="hezqen-ollama-model-prep-$$"
MODELS="${HEZQEN_MODELS:-${RAG_EMBED_MODEL:-nomic-embed-text} ${RAG_CHAT_MODEL:-qwen2.5:0.5b}}"

docker build --pull -f "$PRODUCT_DIR/../local-ai-deployment/Dockerfile.ollama" \
  --build-arg "BASE_IMAGE=ollama/ollama@sha256:910d0d8107b538fb0894e63163eb195de0cc7aefcbc666dc62d3b18f71124592" \
  -t "$OLLAMA_IMAGE" "$PRODUCT_DIR/../local-ai-deployment"
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
