# ADR-0001: No Runtime Coupling to Shared Standards

- Status: Accepted
- Date: 2026-11-15
- Superseded in repository-layout scope by: [ADR-0002](ADR-0002-monorepo.md)

## Context

HEZQEN products share engineering standards. A standards update, tooling outage, or repository permission change must not prevent an already released product from installing or operating. The repository layout must not turn shared standards into a runtime service.

## Decision

HIES is the source of truth for standards, schemas, templates, and development/release tooling. Products may reside in the same monorepo, but their runtime and installation behavior MUST NOT depend on HIES tooling or fetch shared files from a moving branch. Product build pipelines consume the reviewed source tree at an exact commit. Released artifacts are self-contained and carry their required metadata.

## Consequences

- Shared contracts can be maintained centrally without introducing a runtime network dependency.
- Product builds are reproducible from an exact monorepo commit.
- Each product release records its own version and source commit.
- A standards change is reviewed and tested against affected products before release.
- The bundle aggregates immutable product artifacts and manifests rather than copying source directories.

## Rejected alternative

A live standards API or runtime package dependency would introduce availability, version-coupling, and supply-chain risks disproportionate to the benefits of sharing static engineering contracts.
