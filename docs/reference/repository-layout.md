# Reference: repository layout

| Path | Responsibility |
|---|---|
| standards/ | Normative architecture, security, quality, licensing, and operations requirements |
| schemas/ | JSON Schema contracts for product manifests, compatibility, benchmarks, and artifacts |
| scripts/ | Validation, hygiene, release metadata, and checksum tooling |
| products/<id>/ | Independently versioned product source, configuration, tests, documentation, and manifests |
| templates/ | Reusable product threat model, security, support, runbook, and release templates |
| tests/ | Shared validator and product contract regression tests |
| .github/workflows/ | Active repository CI, security, and product runtime workflows |
| workflows/ | Copy-and-adapt workflow templates; not active workflows |
| docs/ | Tutorials, how-to guides, explanations, references, ADRs, and adoption guidance |
| bundle/ | Aggregate bundle documentation and distribution conventions |
| examples/ | Synthetic sample product and release metadata fixtures |

## Product identifiers

| ID | Workspace |
|---|---|
| IK-01 | products/local-ai-deployment/ |
| IK-02 | products/pii-protection/ |
| IK-03 | products/multigpu-optimization/ |
| IK-04 | products/airgapped-rag/ |
| IK-05 | Aggregate bundle manifest/orchestration; not a separate product source workspace |

## Root validation commands

~~~bash
python -m unittest discover -s tests -v
python scripts/validate-schemas.py
python scripts/validate-workflows.py
python scripts/validate-monorepo.py
python scripts/check-repo-hygiene.py .
~~~
