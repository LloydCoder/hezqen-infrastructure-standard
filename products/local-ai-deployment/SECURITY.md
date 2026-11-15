# Security Policy — IK-01

## Supported releases

Security fixes are prioritized for the latest supported product release. Preview builds may change without compatibility guarantees.

## Reporting

Do not open public issues for exploitable vulnerabilities, exposed credentials, or private user data. Use GitHub's private vulnerability reporting for this repository when enabled. If private reporting is unavailable, contact the repository maintainer through a verified private channel listed on the Tinlance website.

Include the affected product version, host platform, Docker/Compose versions, reproduction steps, impact, and sanitized logs. Never include prompts, documents, model weights, session cookies, API keys, or other sensitive data.

## Operator response

1. Restrict network access and preserve relevant logs.
2. Rotate the Open WebUI secret and any exposed credentials.
3. Stop affected services if active exploitation is suspected.
4. Preserve data volumes before destructive remediation.
5. Rebuild from reviewed image digests after a fix is available.
6. Validate restore and access controls before returning to service.
