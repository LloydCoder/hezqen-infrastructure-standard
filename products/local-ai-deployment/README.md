# HEZQEN Local AI Deployment Kit (IK-01)

A hardened, local-first inference workspace using Ollama for model serving and the slim Open WebUI image for the operator interface. The default interface is bound to loopback; the Ollama API is not published to the host. Open WebUI has no direct egress in the default Compose network topology. Embeddings are delegated to Ollama so the UI does not need direct access to external model registries at runtime.

> **Status: engineering preview.** Static CI and a CPU runtime smoke test are implemented for Linux/amd64. A production release still requires non-root container execution or a formally approved exception, immutable image-digest locking, backup/restore drill, SBOM/provenance generation, and security review of the exact upstream images. NVIDIA GPU runtime is not yet verified.

## What is included

- Docker Compose deployment with pinned upstream version tags (never `latest`).
- Ollama model server on a private inference network plus a separate egress network; no host-published API port.
- Open WebUI on the internal-only inference network and bound to `127.0.0.1:3000` by default.
- Slim Open WebUI image with embeddings routed to Ollama.
- Explicit no-tracking environment settings for Open WebUI.
- Persistent named volumes for model and application data.
- Health checks, startup dependency ordering, restart policy, resource limits, dropped Linux capabilities, no-new-privileges, and read-only container root filesystems with explicit writable mounts.
- Optional NVIDIA GPU override.
- Operator guidance for model pulls, backups, updates, rollback, and network exposure.

## Prerequisites

- Linux x86_64 host with Docker Engine and Docker Compose v2 plugin.
- At least 8 GB RAM for the stack; model requirements vary significantly. 16 GB+ RAM is a more practical starting point for small-to-medium quantized models.
- Disk space for container images and model weights.
- For NVIDIA acceleration: supported NVIDIA driver, NVIDIA Container Toolkit, and a Compose implementation supporting device reservations.

## Quick start

```bash
cd products/local-ai-deployment
cp .env.example .env
# Generate a unique secret and paste it into WEBUI_SECRET_KEY in .env.
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
chmod 600 .env
docker compose config --quiet
docker compose up -d
docker compose ps
```

Open `http://127.0.0.1:3000` on the host. Create the first administrator account. Public signup is disabled by default. Do not change the bind address to `0.0.0.0` unless an authenticated VPN or reverse proxy and host firewall policy are in place.

Pull a chat model explicitly after startup:

```bash
docker compose exec ollama ollama pull qwen2.5:7b
```

For document retrieval, also pull the configured embedding model:

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

Model names and hardware requirements change; choose models whose licenses, context windows, quantization, and memory requirements fit your use case. Review model licenses before commercial use.

## NVIDIA GPU

```bash
docker compose -f compose.yaml -f compose.nvidia.yaml config --quiet
docker compose -f compose.yaml -f compose.nvidia.yaml up -d
```

The NVIDIA override grants access to GPU devices only to the Ollama service. The GPU runtime path is opt-in and has not yet passed a physical-device acceptance test.

## Security model

- Default host exposure is loopback only.
- Ollama is reachable by Open WebUI over the internal Compose network, not via a published host port.
- Open WebUI is attached only to an internal Docker network; only Ollama has an egress-capable network for model pulls.
- Open WebUI uses Ollama for embeddings; the slim image avoids bundling the standard local embedding/speech model stack.
- The stack is not an Internet-facing multi-tenant service.
- Both upstream containers run as UID/GID 0 by default. Capabilities are dropped and root filesystems are read-only, but this is not equivalent to non-root execution; stable release is blocked until this is addressed.
- The Docker daemon remains a privileged host control plane; membership in the Docker group is effectively root-equivalent.
- Restrict Ollama egress at the host/network layer to approved registries and model sources where feasible.
- Keep `.env` owner-readable only. Never commit real secrets.
- Do not mount the Docker socket, host root, or broad home directories.
- Back up named volumes before upgrades and test restore procedures.

See [THREAT_MODEL.md](THREAT_MODEL.md), [SECURITY.md](SECURITY.md), [operations](docs/OPERATIONS.md), and [GPU guidance](docs/GPU.md).

## Configuration

See `.env.example`. Change ports, bind address, resource limits, and image tags only after reviewing the threat model and compatibility notes. For production releases, resolve and commit immutable image digests; version tags alone are not sufficient release provenance.

## Verification

From the repository root:

```bash
python3 scripts/validate-manifest.py products/local-ai-deployment/product-manifest.json
python3 scripts/validate-monorepo.py
python3 -m unittest discover -s tests -v
```

The automated runtime smoke test starts the exact CPU Compose stack, verifies health, checks the loopback binding and absence of an Ollama host port, and verifies that the UI can reach Ollama while lacking direct Internet egress. It does not test model inference, NVIDIA GPU operation, ARM64, multi-user load, or production hardening of the host.
