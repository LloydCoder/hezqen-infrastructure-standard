# Configuration Contract Standard

- Configuration MUST be schema-validated before services start.
- Unknown keys MUST be rejected or explicitly reported; they must not be silently ignored where doing so could weaken security.
- Security-sensitive defaults MUST be conservative and documented.
- Configuration examples MUST be safe, synthetic, and non-production.
- Secrets MUST be referenced through secret inputs, not embedded in committed examples.
- Environment-variable names, precedence, types, defaults, and restart requirements MUST be documented.
- Breaking configuration changes require a migration guide and MAJOR version increment.
- A product must provide a way to inspect effective non-secret configuration without disclosing secret values.
