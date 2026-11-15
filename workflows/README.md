# Product Workflow Templates

These files are starting points to copy into each product repository. They are not runtime dependencies and must be reviewed and adapted to the product's language, build system, test suite, and release process.

## Security requirements

- Keep the default token read-only.
- Use a separate job with narrowly scoped write permissions only when a release or security upload requires them.
- Never expose secrets to fork pull requests.
- Do not use `pull_request_target` to check out and execute untrusted pull-request code.
- Pin every third-party action to a verified full-length commit SHA, or use a verified workflow dependency lockfile where supported.
- Avoid privileged self-hosted runners for untrusted pull-request workloads.
- Pin toolchains and dependencies; record their provenance.
- Fail closed when required security checks are unavailable.

## Adoption

Copy the relevant template into the product repository's `.github/workflows/` directory, replace all explicit placeholders, and run a test pull request. Do not copy a template without adapting its permissions, path filters, tool versions, and acceptance criteria.
