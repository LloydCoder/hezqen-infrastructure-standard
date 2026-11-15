# HIES Adoption Guide

## 1. Select a standard version

Choose a tagged HIES release or reviewed commit. Record the exact version and commit in the product repository. Do not follow a moving branch reference.

## 2. Vendor required assets

Copy the applicable schemas, standards, and templates into the product repository. Preserve the upstream version and source commit in an adoption record. Product builds and installations must not fetch this repository.

## 3. Complete product-specific obligations

Every product must supply its own:
- threat model and trust-boundary diagram;
- product manifest and compatibility matrix;
- install, upgrade, rollback, backup, restore, and uninstall procedures;
- license and model-artifact inventory;
- tests and release evidence;
- support and security response policies.

## 4. Record deviations

A deviation must identify the requirement, reason, affected product/version, risk, compensating control, accountable owner, approval, and expiry date. An exception to one product does not apply to another.

## 5. Verify

Run the vendored validators, product CI, security checks, and installation tests. Validate offline behavior where claimed. Record unsupported configurations and tests not run.

## 6. Update

Review adopted HIES assets during product releases and when a security advisory or normative standard change affects the product. Updates are reviewed changes, not automatic runtime downloads.
