# HEZQEN Infrastructure Engineering Standard (HIES)

HIES is the shared engineering contract for the HEZQEN Infrastructure Kits. It defines reusable architecture rules, security baselines, configuration and evidence schemas, testing requirements, release-integrity controls, and CI building blocks.

## Why HIES exists

The four HEZQEN Infrastructure Kits are independently versioned products. They share engineering requirements but must not share a runtime dependency on this repository.

**HIES provides standards, templates, schemas, and workflow building blocks—not a central runtime service.** Product repositories must vendor or pin the relevant HIES assets so they remain buildable and installable if this repository is unavailable.

## Product portfolio

| Product | Repository | Initial scope |
|---|---|---|
| Local AI Deployment Kit | `hezqen-local-ai-deployment-kit` | Secure local inference deployment |
| PII Protection Middleware Kit | `hezqen-pii-protection-kit` | PII detection, redaction, and policy middleware |
| Multi-GPU Optimization Kit | `hezqen-multigpu-optimization-kit` | GPU sizing, parallelism configuration, and benchmarks |
| Air-Gapped RAG Kit | `hezqen-airgapped-rag-kit` | Offline-first retrieval stack and operations |

The infrastructure bundle aggregates compatible product releases; it must not duplicate their codebases.

## Repository map

- `standards/`: normative architecture, security, quality, licensing, and operations requirements.
- `schemas/`: machine-readable product, compatibility, benchmark, and artifact contracts.
- `templates/`: reusable product documentation and operational templates.
- `workflows/`: CI, security, and release workflow building blocks.
- `scripts/`: local validation and release-integrity utilities.
- `tests/`: automated verification for HIES tooling and contracts.
- `docs/`: engineering handbook and lifecycle procedures.

## Security principles

- Least privilege and non-root container execution where supported.
- Explicit inbound/outbound network boundaries.
- No credentials in source, images, examples, or logs.
- Telemetry disabled by default; no prompts, documents, embeddings, secrets, or PII in telemetry.
- Pinned production dependencies and immutable release artifacts.
- Threat models, vulnerability handling, SBOMs, checksums, and verifiable provenance.
- Evidence-based compatibility and performance claims.

See [SECURITY.md](SECURITY.md) for reporting guidance and `standards/security/` for normative requirements.

## Local verification

Requirements: Python 3.10+; no third-party Python dependencies are required for the current validator and unit tests.

```bash
python3 -m unittest discover -s tests -v
python3 -m json.tool schemas/product-manifest.schema.json >/dev/null
python3 scripts/validate-manifest.py path/to/product-manifest.json
```

The manifest validator currently enforces the required HIES product-manifest fields and basic value constraints. JSON Schema files are the machine-readable contract; the Python validator is a dependency-free local preflight, not a complete JSON Schema implementation.

## Adoption

Product repositories should record the HIES version or commit they adopt, vendor the relevant schemas and policy assets, and identify any approved deviations. Do not fetch HIES at product runtime.

## Status

HIES is under active development. A passing repository CI run verifies only the checks currently implemented; it is not a certification, compliance attestation, or proof that every product meets the standard.

## License

Apache-2.0. See [LICENSE](LICENSE).
