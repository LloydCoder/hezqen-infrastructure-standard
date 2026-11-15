# IK-02 Compatibility

- Python runtime: 3.12.
- Container platform declared: Linux amd64.
- HTTP: JSON request body with a top-level `text` property; nested JSON strings are recursively redacted.
- Default listener inside container: `0.0.0.0:8080`; default host publication: `127.0.0.1:8081`.
- Runtime dependencies: Python standard library only.
- The HTTP service supports redact and block actions; HMAC pseudonymization is library-only.
- Host ingress uses a dedicated Docker bridge with IP masquerading disabled; direct Internet egress is runtime-tested.

No regulatory certification or comprehensive PII detection coverage is claimed.
