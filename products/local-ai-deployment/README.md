# HEZQEN Local AI Deployment Kit (IK-01)

A hardened, local-first inference workspace using Ollama for model serving and Open WebUI for the operator interface. The default interface is bound to loopback; the Ollama API is not published to the host.

> **Status: engineering preview.** The compose contract and automated static checks are implemented. A production release still requires host-level runtime testing on supported CPU/GPU platforms, image-digest locking, SBOM/provenance generation, and security review of the exact upstream images.

## What is included

- Docker Compose deployment with pinned upstream version tags (never `latest`).
- Ollama model server on an internal Docker network; no host-published API port.
- Open WebUI bound to `127.0.0.1:3000` by default.
- Persistent named volumes for model and application data.
- Health checks, startup dependency ordering, restart policy, resource limits, dropped Linux capabilities, no-new-privileges, and read-only container root filesystems with explicit writable mounts.
- Optional NVIDIA GPU override.
- Operator guidance for model pulls, backups, updates, rollback, and network exposure.

## Prerequisites

- Linux host with Docker Engine and Docker Compose v2 plugin.
- At least 8 GB RAM for the stack; model requirements vary significantly. 16 GB+ RAM is a more practical starting point for small-to-medium quantized models.
- Disk space for container images and model weights.
- For NVIDIA acceleration: supported NVIDIA driver, NVIDIA Container Toolkit, and a Compose implementation supporting device reservations.

## Quick start

```bash
cd products/local-ai-deployment
cp .env.example .env
# Set a unique WEBUI_SECRET_KEY in .env before starting.
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
# Paste the generated value into .env; protect the file:
chmod 600 .env
docker compose config --quiet
docker compose up -d
docker compose ps
```

Open `http://127.0.0.1:3000` on the host. Create the first administrator account. Public signup is disabled by default. Do not change the bind address to `0.0.0.0` unless an authenticated VPN or reverse proxy and host firewall policy are in place.

Pull a model explicitly after startup:

```bash
docker compose exec ollama ollama pull qwen2.5:7b
```

Model names and hardware requirements change; choose a model whose license, context window, quantization, and memory requirements fit your use case. Review model licenses before commercial use.

## NVIDIA GPU

```bash
docker compose -f compose.yaml -f compose.nvidia.yaml config --quiet
docker compose -f compose.yaml -f compose.nvidia.yaml up -d
```

The NVIDIA override grants access to GPU devices only to the Ollama service. GPU access is a deliberate host-level privilege and must be reviewed for the target machine.

## Security model

- Default host exposure is loopback only.
- Ollama is reachable by Open WebUI over the private Compose network, not via a published host port.
- The stack is not an Internet-facing multi-tenant service.
- The Docker daemon remains a privileged host control plane; membership in the Docker group is effectively root-equivalent.
- Model pulls require outbound network access. Restrict egress at the host/network layer to approved registries and model sources where feasible.
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

Static CI checks do not prove that the stack runs correctly on every host, that a GPU is detected, or that a model fits available VRAM.
