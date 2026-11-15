# Contributing to HEZQEN Infrastructure Standard

Thank you for helping improve HIES. Contributions should make infrastructure products safer, more reproducible, easier to operate, or easier to verify.

## Before you start

- Read the [engineering handbook](docs/engineering-handbook.md) and relevant normative requirements under [standards/](standards/).
- Open an issue before a substantial standards, schema, product-boundary, or release-policy change.
- Keep shared contracts provider-neutral unless a documented product requirement justifies a dependency.
- Never submit credentials, customer data, private keys, access tokens, or production configuration.
- Use synthetic examples and safe-to-run test fixtures.

## Development workflow

1. Fork the repository.
2. Create a focused branch from main, for example docs/clarify-network-boundaries or fix/manifest-validation.
3. Make the smallest coherent change.
4. Update affected standards, schemas, examples, tests, and changelog entries together.
5. Run the relevant checks locally.
6. Push your branch and open a pull request against main.

## Local checks

Use Python 3.12 and install the pinned development dependencies:

~~~bash
python -m pip install --only-binary=:all: -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate-schemas.py
python scripts/validate-workflows.py
python scripts/validate-monorepo.py
python scripts/check-repo-hygiene.py .
~~~

For product-specific changes, also run that workspace's tests and runtime/configuration checks. Docker-based runtime checks may require Linux, Docker Compose v2, Buildx, model downloads, or hardware that is not available in every development environment. State clearly which checks you did not run.

## Standards and code conventions

- Use MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY consistently in normative text.
- A change to a MUST/MUST NOT requirement needs rationale, impact analysis, migration guidance, and an explicit exception strategy where relevant.
- Prefer small, deterministic scripts and machine-readable schemas.
- Validate inputs and fail closed when a failure could expose sensitive data or weaken a security boundary.
- Keep product workspaces independently buildable and releasable.
- Do not introduce runtime or installation-time fetches of HIES or another product's private implementation.
- Pin third-party GitHub Actions to full commit SHAs.
- Document external dependencies, licenses, trust boundaries, and unsupported configurations.

## Pull request requirements

A pull request should explain the problem, scope, affected products/standards/schemas/workflows, security and privacy impact, compatibility and migration implications, tests performed, and known limitations.

All required CI checks must pass. Reviewers should reject unsupported security, compatibility, performance, or compliance claims.

## Commit messages

Use Conventional Commit-style prefixes where practical, such as docs:, fix:, feat:, test:, build:, or security:. This is a convention, not a merge requirement.

## Security reports

Do not report exploitable vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).
