# HEZQEN Local AI Deployment Kit (IK-01)

A hardened, local-first inference workspace using Ollama for model serving and the slim Open WebUI image for the operator interface. Both application containers are built to run as non-root users. The default UI is published only on host loopback; the Ollama API is not published. Open WebUI reaches Ollama over a private inference network and uses a dedicated no-masquerade bridge for loopback ingress, without joining Ollama's egress network.

> **Status: engineering preview.** Static CI and a Linux/amd64 CPU runtime test build and start both non-root images, verify network boundaries, run a small chat model, exercise the embedding API, and test volume backup/restore. A production release still requires SBOM/provenance generation and NVIDIA GPU acceptance testing.

## What is included

- Docker Compose deployment with upstream base images pinned by immutable SHA-256 digest in [images.lock.json](images.lock.json).
- Local non-root derived images: Ollama UID 10002 and Open WebUI UID 10001.
- Ollama on a private inference network plus a separate egress network for model pulls; no host-published API port.
- Open WebUI on the private inference network and a dedicated no-masquerade UI bridge, published to `127.0.0.1:3000` by default.
- Slim Open WebUI image with embeddings routed to Ollama.
- Explicit no-tracking environment settings for Open WebUI.
- Persistent named volumes, checksum-verified backup/restore scripts, and restore smoke tests.
- Health checks, startup dependency ordering, restart policy, resource limits, dropped Linux capabilities, no-new-privileges, and read-only container root filesystems with explicit writable mounts. Open WebUI's generated static assets are copied to its bounded `/tmp` tmpfs via `STATIC_DIR`, avoiding writes to the read-only image filesystem.
- Optional NVIDIA GPU override.
- Operator guidance for model pulls, backups, updates, rollback, and network exposure.

## Prerequisites

- Linux x86_64 Docker host with Docker Engine and Docker Compose v2 plugin.
- Docker BuildKit/buildx support (used to derive non-root images from upstream bases).
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
docker compose build --pull
docker compose up -d --no-build
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

## Backup and restore

```bash
mkdir -p backups
bash scripts/backup.sh "backups/hezqen-ik01-$(date -u +%Y%m%dT%H%M%SZ)"
bash scripts/restore.sh "backups/hezqen-ik01-YYYYMMDDTHHMMSSZ" --confirm
```

Restore requires an explicit confirmation flag and replaces the selected named-volume contents. Backups are not encrypted by the scripts; store them on encrypted storage or encrypt them before off-site transfer. See [operations](docs/OPERATIONS.md).

## NVIDIA GPU

```bash
docker compose -f compose.yaml -f compose.nvidia.yaml config --quiet
docker compose -f compose.yaml -f compose.nvidia.yaml build --pull
docker compose -f compose.yaml -f compose.nvidia.yaml up -d --no-build
```

The NVIDIA override grants access to GPU devices only to the Ollama service. The GPU runtime path is opt-in and has not yet passed a physical-device acceptance test. Device permissions for the non-root Ollama UID may require host-specific group configuration.

## Security model

- Both application containers run as non-root numeric users (Ollama 10002, Open WebUI 10001).
- Upstream base images are pinned by immutable SHA-256 digest; see `images.lock.json`.
- Default host exposure is loopback only.
- Ollama is reachable by Open WebUI over the internal Compose network, not via a published host port.
- Open WebUI is attached to the internal inference network and a dedicated bridge with IP masquerading disabled. It is not attached to the model-egress network.
- Open WebUI uses Ollama for embeddings; the slim image avoids bundling the standard local embedding/speech model stack.
- The runtime smoke workflow verifies that the UI cannot establish direct Internet egress. Host firewall and Docker daemon policy remain part of the trust boundary.
- The stack is not an Internet-facing multi-tenant service.
- The Docker daemon remains a privileged host control plane; membership in the Docker group is effectively root-equivalent.
- Restrict Ollama egress at the host/network layer to approved registries and model sources where feasible.
- Keep `.env` owner-readable only. Never commit real secrets.
- Do not mount the Docker socket, host root, or broad home directories.

See [THREAT_MODEL.md](THREAT_MODEL.md), [SECURITY.md](SECURITY.md), [operations](docs/OPERATIONS.md), and [GPU guidance](docs/GPU.md).

## Configuration

See `.env.example`. Change ports, bind address, resource limits, and image references only after reviewing the threat model and compatibility notes. Do not replace digest-pinned base images with mutable tags in production.

## Verification

From the repository root:

```bash
python3 scripts/validate-manifest.py products/local-ai-deployment/product-manifest.json
python3 scripts/validate-monorepo.py
python3 -m unittest discover -s tests -v
```

The automated runtime smoke test builds the non-root images, starts the CPU Compose stack, verifies process UIDs, health, loopback binding, internal service connectivity, UI egress isolation, a small chat inference, embeddings, and backup/restore. It does not test NVIDIA GPU operation, ARM64, multi-user load, or production hardening of the host.
