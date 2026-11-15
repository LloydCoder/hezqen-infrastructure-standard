# IK-01 Threat Model

## Scope

This model covers the default single-host deployment of Ollama and Open WebUI using Docker Compose. It does not certify the host, Docker daemon, upstream images, downloaded models, reverse proxy, VPN, or external identity provider.

## Assets

- Model weights and model metadata in the Ollama volume.
- Prompts, conversations, uploaded documents, and user records in the Open WebUI volume.
- Web UI signing/session secret.
- Host integrity, Docker daemon control, and network access.

## Trust boundaries

1. Operator workstation to loopback-published Open WebUI.
2. Open WebUI container to Ollama over the Compose bridge.
3. Containers to the host through Docker Engine, mounted volumes, and optional GPU devices.
4. Host to external registries/model sources during image and model downloads.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Remote exposure of inference API | Ollama has no published host port | Docker network/host compromise remains in scope |
| Accidental public UI exposure | Loopback bind default; remote access requires deliberate operator change | Misconfigured bind/proxy/firewall can expose service |
| Unauthorized UI access | Login enabled, public signup disabled, unique secret required | Local account lifecycle and host access remain operator responsibilities |
| Container privilege escalation | Drop capabilities, no-new-privileges, read-only root FS, PID/resource limits | Upstream image process may still run as root; Docker daemon is privileged |
| Data loss | Named persistent volumes and documented backup/restore | Backups can be incomplete or untested |
| Supply-chain compromise | Version-pinned images; release requires digest lock, SBOM, provenance, and review | Upstream publisher compromise and unreviewed model artifacts |
| Malicious or unsafe model artifact | Model/license review and explicit pull workflow | Model behavior and licensing cannot be fully guaranteed |
| Data exfiltration | Local default UI, documented egress control, no telemetry claim | Model pulls and other container egress need host-level restriction |

## Security assumptions and limitations

- The host OS, Docker Engine, operator account, and firewall are trusted and patched.
- Anyone with Docker daemon access is effectively privileged on the host.
- Model download requires outbound connectivity; this kit does not implement a complete egress proxy or network allowlist.
- The upstream images' runtime user and writable-path requirements must be verified for each digest before release. Do not infer non-root operation from this Compose file.
- Do not expose the UI directly to the public Internet. Use a private VPN or an authenticated reverse proxy with TLS and network controls.
- This kit does not guarantee privacy, regulatory compliance, or safe model outputs.
