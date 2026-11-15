# IK-02 Threat Model

## Assets
- Request payloads containing personal or sensitive information.
- Redacted outputs and policy decisions.
- Pseudonymization HMAC key when that action is enabled in the library.
- Runtime integrity and access policy.

## Trust boundaries
- Calling application to the redaction service.
- Host loopback ingress to the container listener.
- Application process to recognizer plugins.
- Container to host kernel and Docker daemon.
- Operator-controlled build environment to runtime image.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Raw PII leaks through logs | HTTP access logging disabled; generic error bodies | Reverse proxies and caller logs must be configured separately |
| Detector crashes and leaks original input | Fail-closed exceptions; no raw payload in error response | Caller may ignore errors; enforce fail-closed at integration boundary |
| Malicious recognizer returns invalid offsets | Span bounds and source-substring validation | Detector implementation remains part of trusted computing base |
| Oversized request exhausts memory | Content-Length limit and bounded body read | Reverse proxy and OS limits also required |
| Unauthorized access | Loopback-only binding by default | No built-in authentication; gateway required for remote access |
| Container compromise | Non-root UID, read-only filesystem, dropped capabilities, no-new-privileges, dedicated no-masquerade bridge | Host kernel and Docker daemon remain trusted |
| Direct container Internet egress | Bridge IP masquerading disabled and runtime egress probe | Host routing/firewall changes or IPv6 configuration may change the boundary |
| Incorrect PII classification | Explicit recognizer coverage and limitations | False negatives and false positives remain possible |
| HMAC key disclosure | Key supplied through library constructor | Key rotation and access controls are operator responsibilities |

## Security assumptions
- Host OS and Docker Engine are trusted and patched.
- Service binds to host loopback by default and is not directly Internet-exposed.
- The dedicated bridge disables IP masquerading; runtime smoke tests direct TCP egress.
- Operators validate the detector corpus and policy before production use.
- A successful redaction response is not proof that every sensitive value was detected.
- The service does not claim GDPR, HIPAA, PCI DSS, NDPR, or other regulatory compliance.

## Residual risks
The default recognizers are not a complete DLP system. They do not perform semantic name/address/medical-entity recognition. No model-based detection is enabled. Downstream applications can still retain or log unredacted inputs if they bypass this service.
