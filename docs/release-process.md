# HIES Release Process

## Change readiness

1. Confirm the change has an issue or documented rationale.
2. Review normative wording and backward compatibility.
3. Validate schemas and examples.
4. Run the complete test suite.
5. Review security and licensing impact.
6. Update CHANGELOG.md.

## Stable release requirements

A stable HIES release must be tagged from a reviewed commit. Release notes identify the standard version, included policies/schemas/workflows, migration impact, and known limitations.

Product repositories must pin the HIES release or commit they adopt. They must vendor the needed files into their own source/release so their build and installation do not depend on HIES availability.

Do not publish a stable release while mandatory validation fails or while material security requirements are ambiguous.


## Metadata and artifact integrity utilities

For a product release artifact directory:

```bash
python scripts/create-release-metadata.py \
  --product your-product-id \
  --version 1.2.3 \
  --source-revision 0123456789abcdef0123456789abcdef01234567 \
  --artifact-dir dist \
  --output dist-artifact-manifest.json

python scripts/validate-release-metadata.py dist-artifact-manifest.json \
  --artifact-root dist
```

The generator records relative paths, media types, byte sizes, and SHA-256 digests. The validator checks the manifest against the HIES JSON Schema and verifies each referenced file. It rejects path traversal, non-portable paths, symlinks, missing files, and content/size mismatches.

These utilities verify integrity against a manifest; they do not authenticate who created the manifest, prove the build source, or replace artifact signing and provenance verification.
