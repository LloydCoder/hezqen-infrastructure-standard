# ADR-0001: HIES Must Not Be a Product Runtime Dependency

- Status: Accepted
- Date: 2026-11-15

## Context

The HEZQEN Infrastructure Kits share engineering standards but are independently versioned products. A central repository outage, deletion, permission change, or incompatible update must not prevent an existing product from installing or operating.

## Decision

HIES is a source-of-truth repository for standards, schemas, templates, and workflow building blocks. Product repositories vendor the required assets at a reviewed commit or release. Products do not fetch HIES during installation or runtime.

## Consequences

- Products remain independently buildable and installable.
- Standards updates require an explicit reviewed adoption change.
- Vendored assets need provenance and version tracking.
- Bundle distribution aggregates product artifacts and manifests rather than duplicating source repositories.

## Rejected alternative

A shared live package or runtime API would introduce availability, version-coupling, and supply-chain risks disproportionate to the benefits of sharing static engineering contracts.
