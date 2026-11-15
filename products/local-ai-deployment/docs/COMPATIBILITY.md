# IK-01 Compatibility Record

## Declared support

- Linux x86_64 Docker hosts.
- Docker Engine with Docker Compose v2 plugin.
- CPU deployment through the base Compose file.
- NVIDIA acceleration through the optional NVIDIA override, subject to host driver and NVIDIA Container Toolkit compatibility. GPU operation is not yet acceptance-tested.

## Upstream components

- Ollama image tag default: `0.40.16`.
- Open WebUI image tag default: `v0.13.2-slim`.

The slim Open WebUI variant is used with Ollama as the embedding engine. Pull the configured `nomic-embed-text` model before enabling document retrieval. These are explicit version tags, not immutable digests. Before a production release, resolve the exact manifest digests for the target architecture, commit a digest lock, record upstream release references, and run the supported-platform matrix. Version tags can be moved by registry publishers.

## Evidence status

- Manifest schema: validated in repository CI.
- Compose YAML and security contract: validated statically in repository CI.
- Linux/amd64 CPU container startup, health, loopback binding, internal service connectivity, and UI egress isolation: exercised by the IK-01 runtime smoke workflow.
- Model inference quality/performance: not yet evidenced by the repository's CI.
- NVIDIA runtime/GPU inference: not yet evidenced.
- ARM64 runtime: not declared supported.
- Backup/restore: documented; restore drill not yet evidenced.
- Non-root container execution: not implemented; both upstream images default to UID/GID 0.
- Immutable image digest lock, SBOM, and signed provenance: release gates, not yet evidenced.

Do not represent undeclared configurations as supported.
