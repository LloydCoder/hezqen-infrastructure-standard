# Product Boundary Standard

Each HEZQEN kit is an independently versioned product with its own source repository, release artifacts, changelog, tests, documentation, and support lifecycle.

Products MUST NOT:
- import or execute code directly from another kit's repository at runtime;
- require the HIES repository to be reachable during installation or operation;
- silently share customer data, credentials, telemetry, or entitlement state;
- claim compatibility with another kit without a tested version matrix.

Cross-product integration uses documented, versioned interfaces and explicit operator configuration. The infrastructure bundle aggregates immutable product releases and manifests; it does not copy or fork product source trees.

Each product owns its product-specific threat model, compatibility evidence, dependencies, and release acceptance.
