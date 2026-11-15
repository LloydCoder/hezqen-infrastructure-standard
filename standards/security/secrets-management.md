# Secrets Management Standard

- Secrets MUST be supplied at runtime through an operator-controlled secret mechanism.
- Credentials MUST NOT be embedded in container images, source code, Compose files, sample configuration, logs, shell history, or release artifacts.
- `.env.example` files MUST contain placeholders only.
- Secret files and environment variables MUST have documented precedence and permissions.
- Applications MUST avoid printing secret values in errors, diagnostics, traces, and crash reports.
- Secrets MUST be rotatable without rebuilding application images where technically feasible.
- Examples MUST use clearly fake values that cannot authenticate to real services.
- CI credentials MUST be scoped to the minimum repository and workflow permissions required.
- Fork pull requests MUST NOT receive privileged secrets.
- Suspected credential exposure MUST trigger revocation/rotation and incident tracking; deleting the exposed text alone is insufficient.
