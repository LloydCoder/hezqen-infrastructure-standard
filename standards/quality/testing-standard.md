# Testing and Verification Standard

## Test layers

1. **Unit/schema:** deterministic logic and contract validation.
2. **Integration:** storage, service boundaries, provider adapters, and containers.
3. **Security:** authorization, network exposure, secrets, data handling, SSRF, path traversal, injection, and trust-boundary enforcement as relevant.
4. **End-to-end:** critical install, operation, backup, restore, upgrade, rollback, and offline flows.
5. **Hardware:** actual declared hardware only; simulated results MUST NOT be represented as hardware compatibility evidence.
6. **Performance:** controlled runs with environment metadata and reproducible commands.

## Requirements

- Every new behavior MUST have a corresponding test.
- Tests MUST be deterministic and isolated.
- A test MUST NOT be skipped merely to obtain a green pipeline.
- Hardware tests unavailable on general CI runners may be recorded as not run, but the corresponding hardware support claim remains unverified.
- Tests MUST assert observable outcomes rather than internal implementation details where practical.
- CI must report skipped, unavailable, and failed tests distinctly.
- Documentation examples that can be executed SHOULD be checked in CI.

## Evidence

Record the source revision, command, environment, dependency versions, result, and limitations for acceptance tests. Performance results must include hardware and workload details.
