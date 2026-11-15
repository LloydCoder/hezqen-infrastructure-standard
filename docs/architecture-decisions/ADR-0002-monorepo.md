# ADR-0002: Monorepo with Independently Versioned Product Workspaces

- Status: Accepted
- Date: 2026-11-15
- Supersedes: the separate-repository layout described in the original MTS baseline and the repository-layout clauses of ADR-0001.

## Context

The initial infrastructure-kit baseline described HIES plus four product repositories and a separate bundle repository. That layout duplicated release coordination, CI policy, schema adoption, dependency maintenance, and cross-product compatibility work. The actual HIES repository already contains the shared standards, schemas, tooling, and CI foundation. The product portfolio is developed and governed by one engineering team and needs atomic changes across shared contracts and product workspaces.

## Decision

Use one monorepo rooted at `LloydCoder/hezqen-infrastructure-standard`.

```text
hezqen-infrastructure-standard/
├── standards/                 # normative shared engineering contracts
├── schemas/                   # shared JSON schemas
├── scripts/                   # validation and release tooling
├── templates/                 # reusable documentation templates
├── workflows/                 # workflow templates (not active workflows)
├── products/
│   ├── local-ai-deployment/   # IK-01
│   ├── pii-protection/         # IK-02
│   ├── multigpu-optimization/ # IK-03
│   └── airgapped-rag/         # IK-04
├── bundle/                    # IK-05 aggregate release metadata/tooling
├── docs/
└── .github/workflows/         # repository CI and security checks
```

Each product workspace MUST own:
- its product manifest and semantic version;
- source/configuration, product-specific tests, documentation, and changelog;
- a threat model and security response instructions;
- compatibility and benchmark evidence;
- license/third-party inventory and release artifacts.

Products MAY share HIES schemas and development tooling at build time. Products MUST NOT import private implementation code from another product, depend on another product's mutable workspace at runtime, or fetch HIES from GitHub during install/operation. Any cross-product integration must use documented, versioned interfaces and explicit operator configuration.

Product versions are independent of the repository version. Use product-scoped tags (`ik01-vX.Y.Z`, `ik02-vX.Y.Z`, etc.) pointing to the exact monorepo commit. Release automation must package only the selected product workspace plus required vendored contracts, and record the full source commit. A change to shared standards triggers the relevant product validation matrix.

The bundle is an aggregate release: it references immutable product artifacts, checksums, SBOMs, provenance, and compatibility evidence. It MUST NOT duplicate product source code.

## Consequences

- One review can update a shared standard and all affected products atomically.
- CI can enforce consistent security, testing, licensing, and release requirements.
- Product releases remain independently versioned and distributable.
- CI must detect which products are affected and validate them; release jobs must package only the selected workspace.
- The former multi-repository MTS layout is retired and must not be used to create four new product repositories.

## Trade-offs

The monorepo increases the impact of repository-level access compromise and can enlarge CI scope. Mitigations include least-privilege access, required review, path-aware CI, CODEOWNERS, product-scoped release permissions, signed provenance, and strict workspace boundaries. These administrative controls must be verified in GitHub settings, not assumed from documentation.
