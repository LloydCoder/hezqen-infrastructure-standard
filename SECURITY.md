# Security Policy

## Scope

This repository contains engineering standards, schemas, templates, validation tooling, and product workspaces for HEZQEN Infrastructure Kits. It is not itself a hosted service. Do not submit customer data, real credentials, private keys, or production secrets in reports.

## Supported versions

The repository is under active engineering preview. Security fixes are applied to the current main branch. Product-specific support status and release versions are maintained in each product workspace's changelog and manifest. Until a stable product release is declared, no long-term maintenance window is promised.

## Report a vulnerability privately

**Do not open a public issue for an exploitable vulnerability or publish a proof of concept before coordinated disclosure.**

Preferred route: [Report a vulnerability privately through GitHub](https://github.com/LloydCoder/hezqen-infrastructure-standard/security/advisories/new). This route depends on GitHub Private Vulnerability Reporting being enabled for the repository.

If the private reporting option is unavailable, contact the maintainer using the verified contact route on the [maintainer's GitHub profile](https://github.com/LloydCoder). Do not guess or use an unverified email address.

Include, where safe: affected product/file/workflow/schema/version/commit; impact and realistic attack prerequisites; minimal reproduction steps or a safe proof of concept; and potential mitigations.

## Response expectations

The maintainer's target is to acknowledge a report within **five business days** and provide an initial severity and scope assessment within **ten business days**. These are response targets, not a guaranteed service-level agreement. Complex reports, holidays, and unavailable reproduction environments may affect timing; the reporter should be kept informed when a material delay occurs.

Confirmed issues are assessed for affected versions, exploitability, severity, remediation, regression coverage, and coordinated disclosure. Remediation timing depends on severity and complexity. A fix is not complete until an appropriate regression check or equivalent verification exists.

## Security expectations

- Treat external inputs, repository content, workflow artifacts, downloaded files, model artifacts, and retrieved documents as untrusted.
- Never execute unreviewed pull-request code with privileged credentials.
- Use least-privilege workflow permissions.
- Pin third-party GitHub Actions to immutable commit SHAs.
- Do not expose secrets to forked pull requests.
- Document accepted risks with an owner, rationale, compensating controls, and expiry date.
- Follow the relevant product threat model and security policy before deploying a product.
