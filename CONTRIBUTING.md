# Contributing to HIES

Thank you for helping improve the HEZQEN Infrastructure Engineering Standard (HIES).

## Contribution rules

- Open an issue before proposing a substantial policy or schema change.
- Keep standards provider-neutral unless a product-specific requirement justifies a dependency.
- Explain the threat, operational impact, compatibility impact, and migration path for normative changes.
- Do not weaken a security requirement merely to make a CI check pass.
- Never commit credentials, customer data, private keys, access tokens, or production configuration.
- Keep examples synthetic and safe to execute.
- Update relevant tests, schemas, examples, and changelog entries together.

## Pull requests

A pull request should include:
1. Problem statement and rationale.
2. Scope and affected standards.
3. Security and privacy impact.
4. Backward-compatibility and migration notes.
5. Verification performed and known limitations.

All required checks must pass. Reviewers should reject unsupported security, compatibility, or performance claims.

## Changes to normative requirements

Use **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** consistently. A MUST/ MUST NOT change requires an explicit rationale and impact analysis. Exceptions must be documented, scoped, time-bounded, and approved by the product owner.
