# Product Workspace Registry

The four products share this monorepo but retain independent manifests, semantic versions, changelogs, compatibility evidence, release tags, and artifact lifecycles.

| ID | Product | Workspace | Status |
|---|---|---|---|
| IK-01 | Local AI Deployment Kit | [local-ai-deployment](local-ai-deployment/) | Engineering preview; CPU runtime workflow verified; GPU and release evidence open |
| IK-02 | PII Protection Middleware Kit | [pii-protection](pii-protection/) | Engineering preview; core unit tests and static deployment contract added; runtime acceptance pending |
| IK-03 | Multi-GPU Optimization Kit | `multigpu-optimization/` | Planned; not yet scaffolded |
| IK-04 | Air-Gapped RAG Kit | `airgapped-rag/` | Planned; not yet scaffolded |

The bundle (IK-05) is a release manifest and installer/orchestration layer over the four products, not a fifth copied codebase.

Do not advertise a planned workspace as available. Engineering preview status is not a stable release or production certification.
