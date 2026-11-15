# IK-02 Operations

## Start
Run `docker compose config --quiet`, then `docker compose up -d --build`. The default host binding is `127.0.0.1:8081`.

## Policy
- `PII_ACTION=redact`: replace detected values with typed placeholders.
- `PII_ACTION=block`: reject a payload when a configured recognizer finds a match.
- `PII_ACTION=pseudonymize`: library-only action requiring an HMAC key. The HTTP service rejects this mode because a secure secret-injection and key-rotation interface is not implemented.

## Data retention
The service is stateless and does not persist request payloads. Configure upstream callers and gateways to avoid retaining raw requests unless required by an approved retention policy.

## Incident response
On detector failure, treat the request as failed and do not retry by sending the original unredacted payload to an alternate destination. Preserve service version and sanitized error context, not raw PII.
