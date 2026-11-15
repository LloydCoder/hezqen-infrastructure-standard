# Security Policy

## Scope

This repository defines standards, schemas, templates, and automation for HEZQEN Infrastructure Kits. It is not itself a hosted service and does not accept customer secrets or production data.

## Reporting a vulnerability

Do not publish exploitable vulnerability details in a public issue. Use GitHub's private vulnerability reporting for this repository when available. If private reporting is unavailable, contact the repository maintainer through a verified private channel listed on the maintainer's GitHub profile.

Include:
- affected file, workflow, schema, or release;
- impact and realistic attack prerequisites;
- minimal reproduction or proof of concept;
- suggested mitigation, if known.

Do not include real credentials, personal data, or customer information.

## Response principles

Reports are triaged by severity and exploitability. Confirmed issues receive a tracked remediation, affected-version assessment, and coordinated disclosure plan. A fix is not considered complete until a regression check or equivalent verification exists.

## Security expectations

- Treat all external inputs, repository content, workflow artifacts, and downloaded files as untrusted.
- Never execute unreviewed pull-request code with privileged credentials.
- Use least-privilege workflow permissions.
- Pin third-party GitHub Actions to immutable commit SHAs before production use.
- Do not expose secrets to forked pull requests.
- Document accepted risks with an owner, rationale, compensating controls, and expiry date.
