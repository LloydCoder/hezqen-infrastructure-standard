# Explanation: HIES repository model

HEZQEN Infrastructure Standard (HIES) is the shared engineering contract and monorepo foundation for four independently versioned infrastructure kits and their aggregate bundle.

## Shared contract, independent products

The root-level standards, schemas, templates, and validation scripts define common requirements. Product implementation remains inside products/<product-id>/. Each product owns its source, configuration, tests, documentation, version, changelog, compatibility evidence, and release lifecycle.

## No runtime coupling

A product may use HIES schemas or validation tooling during development and release preparation from an exact commit. An installed product must not fetch HIES or another product's private implementation at runtime. This keeps product releases reproducible and independently operable.

## Product releases and aggregate bundle

Products are versioned and released independently from the monorepo commit. The aggregate bundle references immutable product artifacts and manifests; it does not copy product source into a second implementation.

## Normative authority

The [standards directory](../../standards/) contains normative requirements. The engineering handbook explains principles, ADRs record architectural decisions, and product documentation explains implementation details. When an explanatory page conflicts with a normative standard, raise the inconsistency for maintainer review rather than silently choosing one.

## Assurance limits

A schema check, passing CI job, checksum, or assurance mapping proves only the property it actually evaluates. None alone establishes production security, regulatory compliance, or certification. Product teams must maintain evidence that matches the product's deployment profile and threat model.
