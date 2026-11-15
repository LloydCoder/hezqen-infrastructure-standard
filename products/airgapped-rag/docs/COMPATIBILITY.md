# IK-04 Compatibility

- Declared target: Linux amd64 with Docker Engine and Docker Compose v2.
- Ollama: 0.40.16 non-root derived image based on the pinned upstream image in the shared IK-01 workspace.
- Qdrant: 1.20.1 unprivileged image, pinned by digest.
- RAG API: Python 3.12.16 slim base image, pinned by digest; runtime uses only the Python standard library.
- Default embedding model: `nomic-embed-text`.
- Default chat model: `qwen2.5:0.5b`.
- Default host API: `127.0.0.1:8090`.
- Offline target install requires the image archive and populated Ollama model archive; it does not pull from registries.

The runtime workflow validates Linux/amd64 only. GPU acceleration, ARM64, high availability, multi-user tenancy, PDF/OCR ingestion, and production backup/restore are not declared supported.
