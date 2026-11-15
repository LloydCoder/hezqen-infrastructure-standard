# IK-01 Compatibility Record

## Declared support

- Linux x86_64 Docker hosts.
- Docker Engine with Docker Compose v2 plugin and BuildKit/buildx.
- CPU deployment through the base Compose file.
- NVIDIA acceleration through the optional NVIDIA override, subject to host driver and NVIDIA Container Toolkit compatibility. GPU operation is not yet acceptance-tested.

## Upstream components

- Ollama base image tag: `ollama/ollama:0.40.16`.
- Open WebUI base image tag: `ghcr.io/open-webui/open-webui:v0.13.2-slim`.
- Product-derived images run as Ollama UID 10002 and Open WebUI UID 10001.

The slim Open WebUI variant is used with Ollama as the embedding engine. Pull the configured `nomic-embed-text` model before enabling document retrieval. These are explicit version tags, not immutable digests. Before a production release, resolve exact manifest digests for target architectures, commit a digest lock, record upstream release references, and run the supported-platform matrix. Version tags can be moved by registry publishers.

## Network design

- Open WebUI attaches to the private inference network and a dedicated UI-ingress bridge with IP masquerading disabled.
- The UI host port is explicitly bound to loopback by default.
- Ollama attaches to the private inference network and a separate egress-capable model-download network.
- The runtime smoke workflow verifies host port publication, UI-to-Ollama connectivity, and lack of direct Internet egress from Open WebUI.

## Evidence status

- Manifest schema: validated in repository CI.
- Compose YAML and security contract: validated statically in repository CI.
- Linux/amd64 CPU container startup, non-root process identity, health, loopback binding, internal service connectivity, and UI egress isolation: exercised by the IK-01 runtime smoke workflow when green on the release candidate commit.
- Model inference quality/performance: not yet evidenced by the repository's CI.
- NVIDIA runtime/GPU inference: not yet evidenced.
- ARM64 runtime: not declared supported.
- Backup/restore: documented; restore drill not yet evidenced.
- Immutable base-image digest lock, SBOM, and signed provenance: release gates, not yet evidenced.

Do not represent undeclared configurations as supported.
