# Security Policy — IK-03

The planner is a local CPU-only CLI and has no network client, credential store, or privileged host integration.

- Treat model identifiers and generated JSON as untrusted inputs/outputs.
- Review generated commands before execution; do not use shell eval on untrusted files.
- Pin package build dependencies and verify release artifacts.
- Do not commit proprietary model metadata or sensitive infrastructure inventory unless approved.
- Report vulnerabilities privately to repository maintainers when private reporting is enabled.
