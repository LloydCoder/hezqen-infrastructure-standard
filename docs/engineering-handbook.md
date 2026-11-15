# HEZQEN Infrastructure Engineering Handbook

## 1. Purpose

The HEZQEN Infrastructure Engineering Standard (HIES) is the shared engineering contract and monorepo foundation for four independently versioned HEZQEN Infrastructure Kits and their aggregate bundle. It provides standards, schemas, templates, and CI/release tooling.

HIES is not a runtime service. Product workspaces live in this repository but must remain independently buildable and installable from a reviewed source commit. Product installations must not fetch HIES or another product workspace at runtime.

## 2. Normative language

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative. A SHOULD deviation requires a documented rationale. A MUST deviation requires a formally approved, scoped, time-bounded exception.

## 3. Architecture principles

1. **Monorepo, independent products:** Each kit owns its version, source/configuration, changelog, tests, release artifacts, and support lifecycle.
2. **Shared standards, no runtime coupling:** Products may consume shared schemas and tooling at build time from an exact commit; runtime/install must not fetch HIES.
3. **Provider neutrality:** Avoid coupling product runtime behavior to a single cloud, payment, telemetry, or model provider.
4. **Local-first operation:** Core runtime functions MUST NOT require HEZQEN accounts, telemetry, or cloud APIs unless explicitly stated in the product manifest.
5. **Explicit network boundaries:** Document every listening port and outbound dependency.
6. **Reproducibility:** Record source revision, dependency versions, image digests, model revisions, hardware, and benchmark conditions as applicable.
7. **No silent upgrades:** Production profiles MUST pin versions and require operator action for upgrades.
8. **Evidence-based claims:** Compatibility claims MUST map to reproducible test evidence.
9. **Safe failure:** Controls protecting sensitive data MUST fail closed where failure could disclose data.
10. **Data minimization:** Telemetry is disabled by default and MUST NOT contain prompts, documents, embeddings, secrets, or personal data.

## 4. Product workspace obligations

Every `products/<product-id>/` workspace MUST maintain:
- a product manifest, independent semantic version, and compatibility record;
- a threat model and documented trust boundaries;
- installation, upgrade, rollback, backup, restore, and uninstall instructions;
- security reporting and support policies;
- third-party and model-license inventories where applicable;
- automated tests for supported behavior;
- release notes, checksums, SBOM, and verifiable provenance for stable releases.

## 5. Release gate

A release is blocked when mandatory tests fail, a critical/high exploitable vulnerability is unresolved without an approved exception, a live secret is detected, a manifest is invalid, required compatibility evidence is missing, licensing is unresolved, or the published artifact differs from the artifact that passed CI.

## 6. Relationship to assurance frameworks

Map relevant controls to NIST SSDF, OWASP ASVS 5.0 for web/API control planes, OWASP Top 10 for LLM Applications 2025 for LLM/RAG risks, and applicable supply-chain assurance practices. A mapping is not a certification or compliance attestation.

## 7. Change management

Normative changes require rationale, impact analysis, migration guidance, and review. Security fixes may be expedited, but must retain traceability and regression evidence.
