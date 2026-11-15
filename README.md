<div align="center">

# HEZQEN Infrastructure Standard

**A provider-neutral engineering contract for teams building, securing, validating, and releasing reproducible AI and infrastructure products.**

[![CI](https://github.com/LloydCoder/hezqen-infrastructure-standard/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/LloydCoder/hezqen-infrastructure-standard/actions/workflows/ci.yml)
[![Security hygiene](https://github.com/LloydCoder/hezqen-infrastructure-standard/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/LloydCoder/hezqen-infrastructure-standard/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

</div>

HEZQEN Infrastructure Standard (HIES) is the shared standards, schemas, templates, and validation layer for four independently versioned infrastructure kits. It helps engineering teams keep product boundaries explicit, security requirements testable, and releases traceable without introducing a runtime dependency on HIES.

> **Project status:** The repository and its four product workspaces are in engineering preview. A passing CI run validates only the checks implemented in that workflow; it is not a security certification or production-readiness attestation.

## Architecture at a glance

~~~mermaid
flowchart TB
    HIES["HIES shared contract"]
    HIES --> ST["standards/"]
    HIES --> SC["schemas/"]
    HIES --> TO["scripts/ and tests/"]
    HIES --> TM["templates/"]
    HIES --> P1["IK-01 Local AI Deployment"]
    HIES --> P2["IK-02 PII Protection"]
    HIES --> P3["IK-03 Multi-GPU Optimization"]
    HIES --> P4["IK-04 Air-Gapped RAG"]
    P1 --> R["Independent product releases"]
    P2 --> R
    P3 --> R
    P4 --> R
    R --> B["IK-05 aggregate bundle manifest"]
~~~

This is a repository architecture map, not a live deployment or product demo. Product-specific usage and runtime evidence are documented in each workspace.

## Why HIES

| Engineering problem | HIES approach |
|---|---|
| Product workspaces drift in structure | Shared manifests, schemas, templates, and validation |
| Security claims are difficult to verify | Normative controls mapped to tests and release evidence |
| Products become coupled at runtime | Shared standards are consumed at build time from an exact commit; no runtime fetch |
| Releases are hard to reproduce | Product-scoped versions, source identity, checksums, SBOM, and provenance requirements |
| Infrastructure assumptions are hidden | Explicit network, configuration, compatibility, and operational contracts |

HIES is intended for engineering teams maintaining multiple infrastructure products or independently releasable deployment kits. It is not a hosted platform, a cloud provider, a compliance certification, or a replacement for product-specific threat modelling.

## Quick Start

Run the shared repository checks from a fresh clone. This validates the contracts and tests; it does not deploy a product.

~~~bash
git clone https://github.com/LloydCoder/hezqen-infrastructure-standard.git
cd hezqen-infrastructure-standard
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --only-binary=:all: -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate-schemas.py
python scripts/validate-monorepo.py
~~~

Python 3.12 is the supported development runtime (.python-version). The dependency file pins the versions used by the repository validation toolchain.

## Installation and prerequisites

HIES is a source repository, not a Python package or runtime service. Clone it and use the shared validation tooling in place.

| Requirement | Purpose |
|---|---|
| Git | Clone and inspect the source revision |
| Python 3.12 | Run validation scripts and unit tests |
| pip | Install pinned development dependencies |
| Docker Engine + Compose v2 | Required only for containerized product workspaces |
| Docker Buildx | Required by selected image-build and runtime acceptance workflows |
| NVIDIA driver + Container Toolkit | Required only for the optional IK-01 GPU profile and hardware-specific validation |

For reproducible local setup, use the pinned Python version and requirements-dev.txt. Product-specific prerequisites are listed in each product README.

## Usage

### Validate a product manifest

~~~bash
python scripts/validate-manifest.py products/local-ai-deployment/product-manifest.json
~~~

### Validate all product workspaces

~~~bash
python scripts/validate-monorepo.py
~~~

### Validate schemas and workflow templates

~~~bash
python scripts/validate-schemas.py
python scripts/validate-workflows.py
~~~

### Run the product test suite

~~~bash
python -m unittest discover -s tests -v
~~~

### Validate a release manifest and its artifacts

~~~bash
python scripts/validate-release-metadata.py examples/sample-product/artifact-manifest.json --artifact-root examples/sample-product/artifacts
~~~

The release metadata command validates the checked-in sample. It does not publish a release or generate provenance.

## Configuration and repository contracts

HIES is configured through version-controlled schemas, product manifests, Compose files, and workflow definitions. It does not load a root .env file or require cloud credentials for shared validation.

| Contract | Location | Purpose |
|---|---|---|
| Product manifest | products/<id>/product-manifest.json | Product identity, version, runtime, and support metadata |
| Manifest schema | schemas/product-manifest.schema.json | Validates product manifest structure |
| Compatibility | schemas/compatibility.schema.json | Describes supported environments and evidence |
| Compatibility matrix | schemas/compatibility-matrix.schema.json | Records compatibility |
| Artifact manifest | schemas/artifact-manifest.schema.json | Describes release artifacts and checksums |
| Benchmark | schemas/benchmark.schema.json | Structures benchmark metadata |
| Development dependencies | requirements-dev.txt | Pins shared validation dependencies |
| Python version | .python-version | Declares the development interpreter version |

Product-specific environment variables and defaults are documented in that product's .env.example and README. Do not assume one product's configuration applies to another.

## Product portfolio

| ID | Product | Workspace | Current evidence and limitations |
|---|---|---|---|
| IK-01 | Local AI Deployment Kit | [products/local-ai-deployment/](products/local-ai-deployment/) | Linux/amd64 CPU runtime, non-root containers, loopback binding, inference and backup/restore smoke tests; physical GPU acceptance remains open |
| IK-02 | PII Protection Middleware Kit | [products/pii-protection/](products/pii-protection/) | Deterministic recognizers and Linux/amd64 API runtime checks; not comprehensive PII detection or a compliance certification |
| IK-03 | Multi-GPU Optimization Kit | [products/multigpu-optimization/](products/multigpu-optimization/) | CPU-only memory estimator and vLLM configuration planner; physical GPU performance evidence is not included |
| IK-04 | Air-Gapped RAG Kit | [products/airgapped-rag/](products/airgapped-rag/) | Offline image/model packaging and disconnected-runtime workflow; review model licenses and single-host limitations |

The aggregate bundle (IK-05) is a manifest and orchestration layer over immutable product artifacts. It is not a fifth product source tree.

## Documentation

| Need | Start here |
|---|---|
| Documentation map | [docs/README.md](docs/README.md) |
| First validation tutorial | [docs/tutorials/first-validation.md](docs/tutorials/first-validation.md) |
| Adopt a product workspace | [docs/how-to/adopt-a-product.md](docs/how-to/adopt-a-product.md) |
| Repository model and design rationale | [docs/explanation/repository-model.md](docs/explanation/repository-model.md) |
| Repository layout reference | [docs/reference/repository-layout.md](docs/reference/repository-layout.md) |
| Engineering handbook | [docs/engineering-handbook.md](docs/engineering-handbook.md) |
| Adoption guide | [docs/adoption-guide.md](docs/adoption-guide.md) |
| Release process | [docs/release-process.md](docs/release-process.md) |
| Assurance mapping | [docs/assurance-mapping.md](docs/assurance-mapping.md) |
| Repository hardening | [docs/repository-hardening.md](docs/repository-hardening.md) |
| Security response process | [docs/security-response-process.md](docs/security-response-process.md) |
| Architecture decisions | [docs/architecture-decisions/](docs/architecture-decisions/) |
| Normative standards | [standards/](standards/) |
| Machine-readable contracts | [schemas/](schemas/) |

The standards/ directory is the normative source. Product READMEs and operational guides explain how individual workspaces implement those requirements.

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), open an issue for substantial policy or schema changes, and include security, compatibility, and migration impact in your pull request. All required checks must pass.

## License and acknowledgements

HIES is distributed under the [Apache License 2.0](LICENSE). Third-party software, container images, and model artifacts retain their own licenses and redistribution conditions; consult each product's licensing inventory and release documentation before redistribution.

## Roadmap

- Complete independently versioned product release automation and evidence publication.
- Expand hardware and platform compatibility evidence.
- Publish verified supply-chain attestations and SBOMs for stable artifacts.
- Improve repository-level security scanning and contributor onboarding.

## Troubleshooting

- If dependency installation fails, confirm Python 3.12 and use the exact pins in requirements-dev.txt.
- If schema validation fails, inspect the reported JSON path and the corresponding schema under schemas/.
- If a product runtime check fails, use that product's operations guide, threat model, and workflow logs.
- Do not treat successful static validation as proof that a product is safe for an exposed production deployment.

## Support

For usage questions and defect reports, use the [issue tracker](https://github.com/LloydCoder/hezqen-infrastructure-standard/issues). For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md) and do not publish exploit details in a public issue.
