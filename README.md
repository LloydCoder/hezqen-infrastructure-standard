# HEZQEN Infrastructure Standard (HIES)

HIES is the shared engineering contract and monorepo for the HEZQEN Infrastructure Kits. It contains reusable standards, schemas, tooling, and four independently versioned product workspaces.

## Repository model

HEZQEN Infrastructure Kits use a **single monorepo**. HIES is the shared standards and tooling layer inside this repository; it is not a runtime service or a product dependency.

- Shared contracts live in `standards/`, `schemas/`, `scripts/`, and `templates/`.
- Product source, manifests, tests, documentation, and release metadata live under `products/<product-id>/`.
- Each product has its own semantic version, changelog, compatibility record, threat model, and release lifecycle.
- Product releases are built from the monorepo commit and published as independently versioned artifacts.
- Product code MUST NOT import another product's private implementation or fetch HIES at install/runtime.
- The bundle is an aggregate distribution of immutable product artifacts and manifests; it does not duplicate product source.

See [ADR-0002: Monorepo with independently versioned products](docs/architecture-decisions/ADR-0002-monorepo.md).

## Product portfolio

| Product | Workspace | Purpose |
|---|---|---|
| Local AI Deployment Kit (IK-01) | `products/local-ai-deployment/` | Hardened local inference deployment using Ollama and Open WebUI |
| PII Protection Middleware Kit (IK-02) | `products/pii-protection/` | PII detection, redaction, and policy middleware |
| Multi-GPU Optimization Kit (IK-03) | `products/multigpu-optimization/` | GPU sizing, parallelism configuration, and benchmarks |
| Air-Gapped RAG Kit (IK-04) | `products/airgapped-rag/` | Offline-first retrieval stack and operations |

The bundle (IK-05) is a release manifest and installer/orchestration layer over the four products, not a fifth copied codebase.

## Repository map

- `standards/`: normative architecture, security, quality, licensing, and operations requirements.
- `schemas/`: machine-readable product, compatibility, benchmark, and artifact contracts.
- `scripts/`: schema, manifest, release-integrity, repository-hygiene, and monorepo validation.
- `products/`: independently versioned product workspaces.
- `templates/`: reusable product documentation and operational templates.
- `workflows/`: copy-and-adapt workflow templates; placeholders are not active release workflows.
- `tests/`: automated verification for shared tooling and product contracts.
- `docs/`: architecture decisions, engineering handbook, assurance mapping, adoption, release, and security response.

## Local verification

Requirements: Python 3.12 and the pinned development dependencies in `requirements-dev.txt`.

```bash
python3 -m pip install --only-binary=:all: -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/validate-schemas.py
python3 scripts/validate-monorepo.py
python3 scripts/validate-manifest.py products/local-ai-deployment/product-manifest.json
```

## Product versioning and releases

Use product-scoped tags (for example, `ik01-v0.1.0`) and a monorepo commit SHA as the source identity. A product release must include its manifest, changelog, compatibility evidence, threat model, SBOM, artifact checksums, provenance, and verified container image digests. Changes to shared standards are adopted through reviewed commits and must not silently alter already-published product artifacts.

## Security and assurance

See [SECURITY.md](SECURITY.md), [repository hardening](docs/repository-hardening.md), and the normative controls under `standards/security/`. A green CI run verifies only the checks implemented by that workflow; it is not a certification, compliance attestation, or production deployment test.

## License

Apache-2.0. See [LICENSE](LICENSE).
