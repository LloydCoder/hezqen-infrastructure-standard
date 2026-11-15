# Product Workspace Registry

The four products share this monorepo but retain independent manifests, semantic versions, changelogs, compatibility evidence, release tags, and artifact lifecycles.

| ID | Product | Workspace | Status |
|---|---|---|---|
| IK-01 | Local AI Deployment Kit | [local-ai-deployment](local-ai-deployment/) | Engineering preview; Linux/amd64 CPU runtime, network boundary, backup/restore, and health acceptance verified; physical GPU and stable release evidence open |
| IK-02 | PII Protection Middleware Kit | [pii-protection](pii-protection/) | Engineering preview; core tests and Linux/amd64 API runtime, redaction, request limits, fail-closed policy, and egress checks verified; broader detection evaluation open |
| IK-03 | Multi-GPU Optimization Kit | [multigpu-optimization](multigpu-optimization/) | Engineering preview; CPU estimator and vLLM configuration-generation tests verified; physical GPU benchmark evidence remains open |
| IK-04 | Air-Gapped RAG Kit | [airgapped-rag](airgapped-rag/) | Engineering preview; offline image/model packaging, checksum verification, disconnected install, local ingestion/retrieval/chat, loopback exposure, and egress acceptance verified on Linux/amd64 CI |
| IK-05 | Complete Infrastructure Lab Bundle | [bundle](../bundle/) | Engineering preview; source-bound offline packaging, manifest/SHA-256 verification, CycloneDX first-party component inventory, safe extraction, and CI artifact acceptance implemented |

IK-05 is a release manifest and installer/orchestration layer over the four products, not a fifth copied codebase.

Do not advertise engineering previews as stable releases. A green workflow proves only the tested platform and checks it executes. Physical GPU performance, broader PII detection quality, signed stable releases, transitive SBOM completeness, legal review, and production certification remain separate evidence gates.
