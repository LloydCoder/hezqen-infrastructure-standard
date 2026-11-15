# Sample Product Threat Model

This is a documentation example, not a production assessment.

## Scope
A static sample package containing metadata and one text artifact. It has no network listener, model runtime, database, or privileged operation.

## Assets
- Product metadata integrity.
- Release artifact integrity.
- Source and release provenance.

## Trust boundaries
- Maintainer-controlled source repository.
- CI runner.
- Generated artifact directory.
- Customer download and verification environment.

## Abuse cases
| Threat | Mitigation | Evidence |
|---|---|---|
| Artifact replaced after manifest generation | SHA-256 manifest and pre-publication verification | `tests/test_release_metadata.py` |
| Manifest path traversal | Reject absolute paths, traversal segments, symlinks, and paths escaping artifact root | `tests/test_release_metadata.py` |
| Invalid product metadata | Validate against Draft 2020-12 schema | `tests/test_schema_validation.py` |

## Limitations
No claim is made about signature authenticity, build provenance, malware absence, or production deployment security.
