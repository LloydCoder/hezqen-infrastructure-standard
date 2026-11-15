# Security Policy — IK-04

- Keep the API bound to host loopback unless an authenticated gateway/VPN is deployed.
- Never publish Qdrant or Ollama ports to the host or Internet.
- Keep the no-masquerade bridge and verify egress isolation after host/network changes.
- Transfer offline bundles through trusted media; verify SHA-256 checksums and separately authenticate the manifest/bundle where required.
- Store volumes and offline media on encrypted storage. The kit does not encrypt data at rest.
- Review model provenance and licenses before preparing the offline bundle.
- Do not ingest sensitive documents unless retention, access, and redaction requirements are approved.
- Treat retrieved content as untrusted and review generated answers.
- Report vulnerabilities privately to repository maintainers when private reporting is enabled.
