# IK-04 Operations

## Connected staging machine
1. Review the image lock and model names in `.env.example`.
2. Build/pull the pinned Ollama, Qdrant, and RAG API images.
3. Run `bash scripts/prepare-models.sh` while connected. The default model set is `nomic-embed-text qwen2.5:0.5b`.
4. Confirm the models appear in `ollama list`.
5. Run `bash scripts/package-offline.sh`.
6. Inspect the generated manifest and checksums; transfer the bundle via approved media.

## Disconnected target
1. Copy the offline bundle to the target.
2. Run `bash install.sh` from the bundle directory.
3. Verify `http://127.0.0.1:8090/healthz`.
4. Ingest a controlled test document, query it, and run a grounded chat test.
5. Confirm no direct Internet egress from the service containers and no host-published Qdrant/Ollama ports.

## Model updates
Repeat the connected staging and packaging workflow for every model update. Treat model files as supply-chain artifacts. Record model name, source, digest, license, and evaluation evidence in the release manifest before transferring.

## Data lifecycle
- Ollama models persist in the `ollama_data` volume.
- Vector collections and payloads persist in `qdrant_storage`.
- Qdrant snapshots persist in `qdrant_snapshots`.
- Back up the named volumes using an approved, encrypted off-host process. The initial release does not provide a production restore orchestrator; validate restore before relying on it.

## Incident response
Stop the stack with `docker compose down`, preserve relevant host/container metadata, and secure offline media. Do not upload documents, prompts, embeddings, model artifacts, or raw logs to external services during investigation unless explicitly approved.
