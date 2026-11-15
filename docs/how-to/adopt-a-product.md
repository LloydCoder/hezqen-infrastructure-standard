# How to adopt or add a product workspace

Use this guide when evaluating an existing kit or proposing a new product workspace.

## Evaluate an existing product

1. Start with the [product registry](../../products/README.md) and the product README.
2. Review its product-manifest.json and the schema in [schemas](../../schemas/).
3. Read the product threat model, security policy, compatibility record, and operations guide.
4. Confirm the exact OS, architecture, container runtime, GPU, model, and dependency versions you intend to use.
5. Run the product's tests and relevant runtime acceptance workflow.
6. Record deviations and unsupported configurations before using the product with sensitive data or production workloads.

## Propose a new product

A new products/<product-id>/ workspace must be independently understandable and releasable. At minimum, prepare:

- A manifest that validates against schemas/product-manifest.schema.json.
- A README, changelog, threat model, security policy, operations guide, and compatibility record.
- Tests for supported behavior and configuration contracts.
- A license and third-party/model artifact inventory where relevant.
- Installation, upgrade, rollback, backup, restore, and uninstall instructions.
- Release evidence appropriate to the product, including source identity, checksums, SBOM, and provenance for stable releases.

Update the monorepo validator and fixtures when introducing a new invariant. Add product-specific CI/runtime workflows where they materially improve assurance.

## Keep boundaries intact

Products may consume shared standards and schemas at build time from the exact source revision. They must not import another product's private implementation or fetch HIES at install/runtime. See [ADR-0001](../architecture-decisions/ADR-0001-no-runtime-coupling.md) and [ADR-0002](../architecture-decisions/ADR-0002-monorepo.md).
