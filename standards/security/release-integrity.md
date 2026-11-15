# Release Integrity Standard

Every stable release MUST include, as applicable:
- CycloneDX JSON SBOM;
- third-party notices and dependency/license inventory;
- SHA-256 checksums for downloadable artifacts;
- signed artifacts or a verifiable signing statement;
- build provenance identifying source revision and workflow identity;
- immutable container image digests;
- vulnerability scan summary and accepted-risk record;
- release notes and known limitations;
- model artifact manifest when models are referenced;
- reproducible build instructions to the extent the toolchain permits.

The artifact delivered to customers MUST be the same artifact that passed the release pipeline. Do not claim SLSA levels, reproducible builds, or cryptographic verification until the relevant properties have been independently verified.
