# Security Policy — IK-02

Report vulnerabilities privately to repository maintainers using GitHub private vulnerability reporting when enabled. Do not include real personal data in public issues.

## Operational requirements
- Keep the service on loopback or a private authenticated network.
- Terminate TLS and authenticate callers at a trusted gateway for remote use.
- Restrict request size and rate at both gateway and service.
- Never log raw request bodies, recognizer matches, or pseudonymization secrets.
- Store HMAC keys in a secret manager; rotate them deliberately.
- Review recognizer coverage and false-negative risk before production use.
- Treat all recognizer plugins as trusted code and pin their dependencies.
