# Network Boundary Standard

Every product MUST document inbound listeners, outbound destinations, protocols, ports, purpose, authentication, data categories, and whether the connection is mandatory or optional.

Defaults:
- Bind administrative, inference, and data services to loopback or a private interface.
- Do not expose vector databases, model runtimes, metrics endpoints, or admin APIs publicly by default.
- Deny unnecessary egress where the deployment environment supports egress controls.
- Separate public ingress from internal service networks.
- Document DNS, package registries, model downloads, license checks, update checks, and telemetry independently.
- Offline and air-gapped modes MUST have an explicit dependency inventory and a testable network-denied acceptance procedure.

Any change that adds a listener or outbound destination requires a threat-model update and release-note disclosure.
