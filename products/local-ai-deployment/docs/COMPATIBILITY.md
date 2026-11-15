# IK-01 Compatibility Record

## Declared support

- Linux x86_64 and ARM64 Docker hosts.
- Docker Engine with Docker Compose v2 plugin.
- CPU deployment through the base Compose file.
- NVIDIA acceleration through the optional NVIDIA override, subject to host driver and NVIDIA Container Toolkit compatibility.

## Upstream components

- Ollama image tag default: `0.40.16`.
- Open WebUI image tag default: `v0.13.2`.

These are explicit version tags, not immutable digests. Before a production release, resolve the exact manifest digests for the target architectures, commit a digest lock, record upstream release references, and run the platform matrix. Version tags can be moved by registry publishers.

## Evidence status

- Manifest schema: validated in repository CI.
- Compose YAML and security contract: validated statically in repository CI.
- Runtime CPU deployment: not yet evidenced by the repository's CI.
- NVIDIA runtime/GPU inference: not yet evidenced.
- ARM64 runtime: not yet evidenced.
- Backup/restore: documented; restore drill not yet evidenced.
- Immutable image digest lock, SBOM, and signed provenance: release gates, not yet evidenced.

Do not represent undeclared configurations as supported.
