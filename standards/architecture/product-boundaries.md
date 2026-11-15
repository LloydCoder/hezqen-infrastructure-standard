# Product Boundary Standard

HEZQEN infrastructure products are independently versioned workspaces within the shared monorepo. A monorepo is a source-control and governance choice; it does not authorize runtime coupling.

Each product MUST own its source/configuration, manifest, version, changelog, tests, threat model, compatibility evidence, dependency inventory, release artifacts, and support lifecycle.

Products MUST NOT:
- import or execute private implementation code directly from another product workspace;
- require HIES validation tooling or the GitHub repository to be reachable during installation or operation;
- silently share customer data, credentials, telemetry, or entitlement state;
- claim compatibility with another kit without a tested version matrix;
- use mutable branch references as release dependencies.

Products MAY consume shared schemas, templates, and development tooling at build time from the exact monorepo commit. Released artifacts MUST be self-contained and MUST record their source commit and adopted standard version.

Cross-product integration uses documented, versioned interfaces and explicit operator configuration. The infrastructure bundle aggregates immutable product releases, manifests, checksums, SBOMs, provenance, and compatibility evidence; it does not copy product source trees.

A product release is identified by a product-scoped semantic version and a tag such as `ik01-v0.1.0`. A repository commit may contain changes to multiple products, but each product's release notes and artifacts must describe only that product's shipped changes.
