# HIES Adoption Guide

## 1. Select the shared contract revision

In this monorepo, product workspaces consume shared HIES standards, schemas, and tooling from the exact commit being built. Record the HIES revision in the product release metadata. Do not fetch standards from a moving branch during installation or runtime.

## 2. Maintain product boundaries

Each `products/<product-id>/` workspace owns its manifest, version, changelog, source/configuration, tests, threat model, compatibility evidence, license inventory, and release documentation. Shared schemas and validation tooling may be used at build time.

## 3. Complete product-specific obligations

Every product must supply its own:
- threat model and trust-boundary description;
- product manifest and compatibility matrix;
- install, upgrade, rollback, backup, restore, and uninstall procedures;
- license and model-artifact inventory;
- tests and release evidence;
- support and security response policies.

## 4. Record deviations

A deviation must identify the requirement, reason, affected product/version, risk, compensating control, accountable owner, approval, and expiry date. An exception to one product does not apply to another.

## 5. Verify

Run shared schema and repository checks plus product-specific tests and installation checks. Validate offline behavior where claimed. Record unsupported configurations and tests not run. A passing static configuration check is not a runtime deployment test.

## 6. Release independently

Use product-scoped semantic versions and tags. Package only the selected product workspace and required self-contained assets. Include the source commit, adopted HIES revision, SBOM, checksums, provenance, compatibility evidence, and release notes. The bundle references immutable product artifacts rather than duplicating source.

## 7. Update

Review shared standards and product workspaces together. Security advisories and normative standard changes trigger impact analysis for all affected products; they do not automatically change already published artifacts.
