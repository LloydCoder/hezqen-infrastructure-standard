# HEZQEN Air-Gapped Local RAG Kit (IK-04)

An offline-first local retrieval-augmented generation stack built from Ollama, Qdrant, and a small Python API. It provides document ingestion, chunking, local embeddings, vector retrieval, and grounded local chat. The deployment includes an image/model export workflow and a target-side installer that loads local artifacts without pulling from a registry.

> **Status: engineering preview.** The default profiles use the small `nomic-embed-text` and `qwen2.5:0.5b` models for acceptance testing. Review model licenses and use-case suitability before production. This is a single-host local stack, not a highly available multi-tenant platform.

## Architecture

- **Ollama** runs local embedding and chat models. Its API is not published to the host.
- **Qdrant** stores vectors and document payloads. Its REST/gRPC ports are not published.
- **RAG API** accepts local requests, chunks and embeds documents, performs vector search, and generates answers with source references.
- All containers share a dedicated Docker bridge with IP masquerading disabled. Only the RAG API is published, bound to host loopback by default.
- Persistent Ollama model and Qdrant data volumes are kept separate.

## Two-stage deployment

### 1. Prepare artifacts on a connected staging machine

This phase requires registry/model access. It is deliberately separate from the air-gapped target.

```bash
cd products/airgapped-rag
bash scripts/prepare-models.sh
bash scripts/package-offline.sh
```

The model-preparation script downloads the configured models into the Ollama volume. The packaging script builds/pulls the pinned container images, exports images and model volume data, writes a manifest, and generates SHA-256 checksums.

Copy the generated `dist/hezqen-airgapped-rag-offline-0.1.0/` directory to approved offline media. The bundle contains the deployment Compose file, environment example, image archive, model archive, manifest, checksums, installer, and instructions.

### 2. Install on the disconnected target

Copy the offline bundle to the target, then run:

```bash
cd hezqen-airgapped-rag-offline-0.1.0
bash install.sh
```

The installer verifies all checksums, loads Docker images from the local archive, restores the model volume, initializes Qdrant volume ownership, and starts Compose with `--pull never`. It does not invoke `docker pull`, access a model registry, or require Internet connectivity.

Open `http://127.0.0.1:8090/healthz` on the host after installation.

## API

Ingest documents:

```bash
curl -sS http://127.0.0.1:8090/v1/ingest \
  -H 'Content-Type: application/json' \
  -d '{"documents":[{"id":"handbook-1","text":"HEZQEN is a local-first intelligence and infrastructure toolkit."}]}'
```

Search:

```bash
curl -sS http://127.0.0.1:8090/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is HEZQEN?","top_k":4}'
```

Grounded chat:

```bash
curl -sS http://127.0.0.1:8090/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is HEZQEN?","top_k":4}'
```

The API returns source IDs and similarity scores. The system prompt treats retrieved content as untrusted reference material and instructs the model to ignore instructions embedded in documents. This mitigates but does not eliminate retrieval/prompt-injection risk.

## Security boundaries

- Default host binding is `127.0.0.1:8090`.
- Ollama and Qdrant have no host-published ports.
- Containers run as non-root users with read-only root filesystems, dropped capabilities, and no-new-privileges.
- Docker bridge IP masquerading is disabled; runtime tests verify that the RAG API cannot reach the public Internet.
- No API authentication is included. Keep the service local. If remote access is required, use an authenticated gateway/VPN and a host firewall.
- The kit does not encrypt model/data volumes itself. Use encrypted disks and protect offline media.

## Verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
docker compose config --quiet
```

See [offline bundle format](docs/OFFLINE-BUNDLE.md), [operations](docs/OPERATIONS.md), [compatibility](docs/COMPATIBILITY.md), and [THREAT_MODEL.md](THREAT_MODEL.md).
