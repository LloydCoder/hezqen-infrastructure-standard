# Repository Hardening Checklist

This checklist applies to the HIES monorepo. Repository settings are administrative controls and must be verified in GitHub settings; workflow files alone cannot enforce all of them.

## Branch protection for main

- Require a pull request before merging.
- Require at least one approving review; dismiss stale approvals after new commits.
- Require approval of the most recent reviewable push where available.
- Require conversation resolution.
- Require status checks: `Validate shared contracts and product workspaces` and `Scan tracked working tree for obvious credential patterns`.
- Require branches to be up to date before merging.
- Block force pushes and branch deletion.
- Apply rules to administrators where operationally appropriate.
- Restrict direct pushes to the smallest maintainer set.

## Repository security settings

- Enable secret scanning and push protection where available.
- Enable Dependabot alerts and security updates.
- Enable private vulnerability reporting.
- Restrict Actions to approved actions; prefer SHA-pinned dependencies.
- Set the default workflow token permission to read-only.
- Disable unnecessary GitHub Pages, package publishing, and deploy environments.
- Protect release environments with required reviewers if release publishing is enabled.
- Use CODEOWNERS and product-scoped release permissions where available.

## Verification record

Record the date, reviewer, settings inspected, and any unavailable controls. Do not mark a control implemented solely because it is documented here.
