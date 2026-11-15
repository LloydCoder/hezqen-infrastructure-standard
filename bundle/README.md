# HEZQEN Infrastructure Lab Bundle (IK-05)

IK-05 is an offline aggregate distribution of IK-01 through IK-04. It packages each product workspace once, preserves independent product versions and licenses, and does not duplicate product source in a second implementation.

## Build

From the repository root with Python 3.12:

```bash
python scripts/bundle.py build --output ./dist/hezqen-infrastructure-bundle --source-revision "$(git rev-parse HEAD)"
```

The builder creates:
- one versioned `.tar.gz` archive per product;
- `bundle-manifest.json` bound to the full source commit, product versions, licenses, platforms, archive sizes, and SHA-256 digests;
- `sbom.cdx.json`, a CycloneDX 1.6 inventory of the four first-party product components;
- `SHA256SUMS` covering the generated manifest, SBOM, and product archives.

## Verify and install offline

```bash
python scripts/bundle.py verify ./dist/hezqen-infrastructure-bundle
python scripts/bundle.py install ./dist/hezqen-infrastructure-bundle --destination ./hezqen-installed
```

The verifier checks the source revision format, complete product inventory, archive checksums and sizes, product identity/version/license consistency, archive member paths and types, and SBOM structure. The installer performs no network access, rejects unsafe archive members, refuses to overwrite existing product directories, and extracts each product into `<destination>/products/<product-id>`.

## CI acceptance

The `IK-05 Offline Bundle Acceptance` workflow builds the distribution from the exact CI commit, runs bundle regression tests, verifies it, installs it into a clean directory, checks the installed inventory, and uploads the resulting bundle as a workflow artifact.

## Assurance limits

The SBOM currently inventories the four HEZQEN product components; it is not a complete transitive dependency SBOM. Workflow artifact upload is not a cryptographic signature or long-term immutable release. Stable commercial releases still require signed provenance, full dependency SBOMs, immutable release hosting, legal/license review, and a tested compatibility matrix. This bundle is an engineering-preview distribution, not a production certification.
