# Logging and Data Minimization Standard

## Defaults

Telemetry MUST be disabled by default or local-only. Products MUST operate without sending data to HEZQEN.

Logs MUST NOT contain:
- passwords, access tokens, API keys, private keys, or session cookies;
- raw prompts or model responses by default;
- document contents, embeddings, or customer payloads;
- unnecessary personal or sensitive information.

## Operational requirements

- Use structured logs with documented fields and severity.
- Redact sensitive values before logs leave the process.
- Document log locations, retention, rotation, and deletion.
- Make diagnostic bundles opt-in and previewable before export.
- Document every outbound telemetry destination and data category.
- Provide an operator-accessible way to disable optional telemetry.
- Avoid stable cross-customer identifiers unless strictly necessary and explicitly disclosed.

Security and audit events should record the action, outcome, timestamp, and relevant non-sensitive actor/resource identifiers without recording secrets or payload contents.
