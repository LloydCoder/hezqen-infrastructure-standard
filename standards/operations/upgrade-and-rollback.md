# Upgrade and Rollback Standard

- Production dependencies and container images MUST be pinned.
- Upgrades MUST be explicit operator actions; automatic silent upgrades are prohibited.
- Each upgrade guide MUST list preconditions, backup requirements, expected downtime, data migrations, and rollback constraints.
- Destructive or irreversible migrations MUST be identified before execution.
- Rollback MUST be tested where technically possible; otherwise document the reason and a recovery alternative.
- Upgrade tooling MUST display the target version and material changes before applying them.
- A failed upgrade MUST leave the previous known-good state recoverable or provide a documented recovery path.
