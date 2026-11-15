# Product Workspace Registry

The four products share this monorepo but retain independent manifests, semantic versions, changelogs, compatibility evidence, release tags, and artifact lifecycles.

| ID | Product | Workspace | Status |
|---|---|---|---|
| IK-01 | Local AI Deployment Kit | [local-ai-deployment](local-ai-deployment/) | Engineering preview; static CI green, runtime/release gates open |
| IK-02 | PII Protection Middleware Kit | `pii-protection/` | Planned; not yet scaffolded |
| IK-03 | Multi-GPU Optimization Kit | `multigpu-optimization/` | Planned; not yet scaffolded |
| IK-04 | Air-Gapped RAG Kit | `airgapped-rag/` | Planned; not yet scaffolded |

Do not treat a planned workspace as an implemented product or advertise it as available. Product status changes only when its implementation and evidence are committed.
