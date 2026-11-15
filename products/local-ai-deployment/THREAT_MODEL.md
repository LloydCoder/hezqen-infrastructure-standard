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
2. Open WebUI container to Ollama over the internal-only Compose network.
3. Ollama container to the model-egress network for model downloads.
4. Containers to the host through Docker Engine, mounted volumes, and optional GPU devices.
5. Host to external registries/model sources during image and model downloads.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Remote exposure of inference API | Ollama has no published host port | Docker network/host compromise remains in scope |
| Accidental public UI exposure | Loopback bind default; remote access requires deliberate operator change | Misconfigured bind/proxy/firewall can expose service |
| Unauthorized UI access | Login enabled, public signup disabled, unique secret required | Local account lifecycle and host access remain operator responsibilities |
| UI container data exfiltration | Open WebUI is attached only to an internal Docker network; explicit no-tracking settings | Host compromise, browser-side exposure, or future config changes remain possible |
| Model server egress | Only Ollama is attached to the model-egress network | Egress is not allowlisted by this Compose file; enforce policy at host/network layer |
| Container privilege escalation | Drop capabilities, no-new-privileges, read-only root FS, PID/resource limits | Both upstream images default to UID/GID 0; Docker daemon is privileged |
| Data loss | Named persistent volumes and documented backup/restore | Backups can be incomplete or untested |
| Supply-chain compromise | Version-pinned images; release requires digest lock, SBOM, provenance, and review | Upstream publisher compromise and unreviewed model artifacts |
| Malicious or unsafe model artifact | Model/license review and explicit pull workflow | Model behavior and licensing cannot be fully guaranteed |

## Security assumptions and limitations

- The host OS, Docker Engine, operator account, and firewall are trusted and patched.
- Anyone with Docker daemon access is effectively privileged on the host.
- Model download requires outbound connectivity. The Ollama service has an egress-capable network; this kit does not implement a complete registry/model-source allowlist.
- Open WebUI has no direct container egress in the default topology. Verify this with the runtime smoke workflow.
- The upstream Ollama and Open WebUI images run as UID/GID 0 by default. Capabilities are dropped, but non-root execution is not claimed. A reviewed non-root image build or a formally approved time-bounded exception is required before stable production release.
- Do not expose the UI directly to the public Internet. Use a private VPN or an authenticated reverse proxy with TLS and network controls.
- This kit does not guarantee privacy, regulatory compliance, or safe model outputs.
