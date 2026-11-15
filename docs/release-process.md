# HIES and Product Release Process

## 1. Shared-standard change readiness

1. Confirm the change has an issue or documented rationale.
2. Review normative wording and backward compatibility.
3. Validate schemas and examples.
4. Run the complete test suite and all affected product checks.
5. Review security and licensing impact.
6. Update the shared changelog and migration guidance.

## 2. Independent product release readiness

A product release is identified by its own semantic version and product-scoped tag (for example, `ik01-v0.1.0`). It does not require a repository-wide version bump.

Before tagging:
1. Validate the selected product manifest and workspace.
2. Run shared CI plus all product-specific tests and supported-platform acceptance tests.
3. Review the threat model, upstream component versions, licenses, vulnerability findings, and deviations.
4. Resolve container image references to immutable digests and record architecture-specific manifests.
5. Generate the product SBOM, checksums, release manifest, and verifiable build provenance.
6. Verify backup/restore and upgrade/rollback where persistent state exists.
7. Publish only the selected product's self-contained artifact and documentation.

A product tag must point to the exact monorepo commit used to build the artifact. The release record identifies the product ID, product version, source commit, HIES contract revision, image/model digests, and evidence bundle.

## 3. Bundle release

The infrastructure bundle aggregates immutable product artifacts, manifests, checksums, SBOMs, provenance, and compatibility evidence. It MUST NOT copy product source directories or rebuild products implicitly. Bundle compatibility is declared as an explicit product-version matrix.

## 4. Stable release requirements

Do not publish a stable release while mandatory validation fails or while material security requirements are ambiguous. Product workspaces may be released independently; shared standards changes are released separately and adopted through reviewed source commits.

## 5. Metadata and artifact integrity utilities

From the repository root, for a product artifact directory:

```bash
python scripts/create-release-metadata.py \
  --product local-ai-deployment \
  --version 0.1.0 \
  --source-revision 0123456789abcdef0123456789abcdef01234567 \
  --artifact-dir products/local-ai-deployment/dist \
  --output products/local-ai-deployment/dist-artifact-manifest.json

python scripts/validate-release-metadata.py \
  products/local-ai-deployment/dist-artifact-manifest.json \
  --artifact-root products/local-ai-deployment/dist
```

The generator records relative paths, media types, byte sizes, and SHA-256 digests. The validator checks the manifest against the HIES JSON Schema and verifies each referenced file. It rejects path traversal, non-portable paths, symlinks, missing files, and content/size mismatches.

These utilities verify integrity against a manifest; they do not authenticate who created the manifest, prove the build source, or replace artifact signing and provenance verification.
