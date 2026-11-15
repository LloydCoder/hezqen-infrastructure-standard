# IK-01 Compatibility Record

## Declared support

- Linux x86_64 Docker hosts.
- Docker Engine with Docker Compose v2 plugin and BuildKit/buildx.
- CPU deployment through the base Compose file.
- NVIDIA acceleration through the optional NVIDIA override, subject to host driver and NVIDIA Container Toolkit compatibility. GPU operation is not yet acceptance-tested.

## Upstream components and immutable digests

- Ollama base: `ollama/ollama:0.40.16`, digest `sha256:910d0d8107b538fb0894e63163eb195de0cc7aefcbc666dc62d3b18f71124592`.
- Open WebUI base: `ghcr.io/open-webui/open-webui:v0.13.2-slim`, digest `sha256:ea9fee9b0d83a4d73f5ddb7e23ccf42bc3514aaebc7382247af1287871397140`.
- Product-derived images run as Ollama UID 10002 and Open WebUI UID 10001.

The slim Open WebUI variant is used with Ollama as the embedding engine. Pull the configured `nomic-embed-text` model before enabling document retrieval. Digests are recorded in `images.lock.json` and checked by the runtime workflow. A base-image update requires a reviewed lock-file change and a new runtime acceptance run.

## Network design

- Open WebUI attaches to the private inference network and a dedicated UI-ingress bridge with IP masquerading disabled.
- The UI host port is explicitly bound to loopback by default.
- Ollama attaches to the private inference network and a separate egress-capable model-download network.
- The runtime smoke workflow verifies host port publication, UI-to-Ollama connectivity, and lack of direct Internet egress from Open WebUI.

## Evidence status

- Manifest schema: validated in repository CI.
- Compose YAML, image lock, and security contract: validated statically in repository CI.
- Linux/amd64 CPU container startup, non-root process identity, health, loopback binding, internal service connectivity, and UI egress isolation: exercised by the IK-01 runtime smoke workflow.
- CPU generation with `qwen2.5:0.5b` and embedding response with `nomic-embed-text`: exercised by the runtime smoke workflow.
- NVIDIA runtime/GPU inference: not yet evidenced.
- ARM64 runtime: not declared supported.
- Backup/restore: documented; restore drill not yet evidenced.
- SBOM and signed provenance: release gates, not yet evidenced.

Do not represent undeclared configurations as supported.
