#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

PRODUCT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$PRODUCT_DIR"

OLLAMA_IMAGE="${OLLAMA_IMAGE:-hezqen/ollama:0.40.16-nonroot}"
QDRANT_IMAGE="${QDRANT_IMAGE:-qdrant/qdrant:v1.20.1-unprivileged@sha256:d18c8e5061be3eaea2f53fbee1f0bf0382dc59cbb9b7112e41ffcc937ec14220}"
RAG_API_IMAGE="${RAG_API_IMAGE:-hezqen/airgapped-rag-api:0.1.0}"
OLLAMA_VOLUME="${OLLAMA_VOLUME:-hezqen-airgapped-rag_ollama_data}"
BUNDLE_ROOT="${1:-$PRODUCT_DIR/dist}"
BUNDLE_DIR="$BUNDLE_ROOT/hezqen-airgapped-rag-offline-0.1.0"

docker volume inspect "$OLLAMA_VOLUME" >/dev/null
docker build --pull -f ../local-ai-deployment/Dockerfile.ollama \
  --build-arg "BASE_IMAGE=ollama/ollama@sha256:910d0d8107b538fb0894e63163eb195de0cc7aefcbc666dc62d3b18f71124592" \
  -t "$OLLAMA_IMAGE" ../local-ai-deployment
docker build --pull -f Dockerfile.api -t "$RAG_API_IMAGE" .
docker pull "$QDRANT_IMAGE"

docker run --rm --network none --user 10002:10002 \
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/home/ollama/.ollama,readonly" \
  --entrypoint /bin/bash "$OLLAMA_IMAGE" -lc \
  'test -d /home/ollama/.ollama/models/manifests && find /home/ollama/.ollama/models/manifests -type f | grep -q .'

rm -rf -- "$BUNDLE_DIR"
mkdir -p -- "$BUNDLE_DIR"
docker save -o "$BUNDLE_DIR/images.tar" "$OLLAMA_IMAGE" "$QDRANT_IMAGE" "$RAG_API_IMAGE"

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$OLLAMA_VOLUME,dst=/source,readonly" \
  --entrypoint /bin/bash "$OLLAMA_IMAGE" -lc 'tar -czf - -C /source .' > "$BUNDLE_DIR/models.tar.gz"

cp compose.yaml .env.example README.md images.lock.json "$BUNDLE_DIR/"
cp scripts/install-offline.sh "$BUNDLE_DIR/install.sh"

python3 - "$BUNDLE_DIR" "$OLLAMA_IMAGE" "$QDRANT_IMAGE" "$RAG_API_IMAGE" "${HEZQEN_MODELS:-nomic-embed-text qwen2.5:0.5b}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

directory, ollama, qdrant, rag_api, models = sys.argv[1:]
manifest = {
    "schemaVersion": "1.0.0",
    "product": "airgapped-rag",
    "productVersion": "0.1.0",
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "platform": "linux/amd64",
    "images": {"ollama": ollama, "qdrant": qdrant, "ragApi": rag_api},
    "models": models.split(),
    "embeddingModel": __import__("os").getenv("HEZQEN_EMBED_MODEL", "nomic-embed-text"),
    "chatModel": __import__("os").getenv("HEZQEN_CHAT_MODEL", "qwen2.5:0.5b"),
    "artifacts": ["images.tar", "models.tar.gz", "compose.yaml", ".env.example", "images.lock.json", "install.sh", "README.md"],
}
(Path(directory) / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

(
  cd "$BUNDLE_DIR"
  sha256sum images.tar models.tar.gz manifest.json images.lock.json compose.yaml .env.example install.sh README.md > SHA256SUMS
  chmod 600 images.tar models.tar.gz manifest.json SHA256SUMS
)
echo "Offline deployment bundle created: $BUNDLE_DIR"
