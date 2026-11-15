# Schema Registry

These JSON Schema documents are versioned public contracts for HEZQEN product and release metadata.

- `product-manifest.schema.json`: product identity, version, license, runtime, and metadata.
- `compatibility.schema.json`: one tested environment/result record.
- `compatibility-matrix.schema.json`: compatibility records grouped by product version.
- `benchmark.schema.json`: reproducible benchmark metadata and measurements.
- `artifact-manifest.schema.json`: release artifact hashes and related integrity metadata.

Schema changes are contract changes. Document compatibility and migration impact before modifying a released schema. Draft 2020-12 is used.
