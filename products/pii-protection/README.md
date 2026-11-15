# HEZQEN PII Protection Middleware Kit (IK-02)

A dependency-free, local-first JSON PII redaction service and Python library. It provides a small deterministic recognizer set, a pluggable detector contract, nested JSON processing, redaction/block/pseudonymization policies, and fail-closed handling.

> **Status: engineering preview.** Built-in recognizers cover email addresses, Luhn-valid payment-card candidates, phone-like strings, and IPv4 addresses. This is not comprehensive PII detection and is not a compliance certification. Validate recognizers against target languages, data formats, and jurisdictions before processing sensitive production data.

## Quick start

```bash
cd products/pii-protection
docker compose config --quiet
docker compose build
docker compose up -d
curl -sS http://127.0.0.1:8081/healthz
curl -sS http://127.0.0.1:8081/v1/redact -H 'Content-Type: application/json' -d '{"text":"Contact a.person@example.com"}'
```

The service binds to loopback by default on a dedicated Docker bridge with IP masquerading disabled. Do not expose it directly to the Internet. Put authentication, authorization, TLS, request limits, and audit policy at a trusted gateway before allowing other hosts to call it.

## Library use

```python
from hezqen_pii import RedactionEngine

engine = RedactionEngine()
safe_text = engine.redact("Email me at a.person@example.com")
safe_payload = engine.redact_json({"customer": {"email": "a.person@example.com"}})
```

Use `action="block"` to reject payloads when configured PII is found. Use `action="pseudonymize"` with a high-entropy HMAC key supplied by a secret manager for deterministic tokens. The HTTP service intentionally supports only redact/block until a secure key-injection and rotation contract is implemented.

## Fail-closed behavior

- Detector exceptions and invalid detection spans raise `RedactionError`.
- The HTTP service does not echo request content, recognizer errors, or raw PII in error responses.
- Unsupported JSON values are rejected.
- Block policy raises `PiiPolicyViolation` when a configured recognizer finds a match.
- There is no implicit fallback to returning the original payload.

## Detection limitations

Regex recognizers are precision-oriented and language-limited. Names, addresses, national identifiers, free-form medical data, context-dependent identifiers, images, audio, and many domain-specific identifiers are not comprehensively detected. False positives and false negatives are expected. Use a reviewed recognizer inventory and representative evaluation corpus.

## Verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
docker compose config --quiet
```

See [THREAT_MODEL.md](THREAT_MODEL.md), [SECURITY.md](SECURITY.md), and [docs/OPERATIONS.md](docs/OPERATIONS.md).
