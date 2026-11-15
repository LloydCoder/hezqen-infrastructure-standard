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
2. Open WebUI container to Ollama over the internal-only inference network.
3. Open WebUI host ingress through a dedicated bridge network with IP masquerading disabled.
4. Ollama container to the model-egress network for model downloads.
5. Non-root application processes to the host through Docker Engine, mounted volumes, and optional GPU devices.
6. Host to external registries/model sources during image and model downloads.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Remote exposure of inference API | Ollama has no published host port | Docker network/host compromise remains in scope |
| Accidental public UI exposure | Loopback bind default; dedicated ingress bridge defaults to loopback | Misconfigured bind/proxy/firewall can expose service |
| Unauthorized UI access | Login enabled, public signup disabled, unique secret required | Local account lifecycle and host access remain operator responsibilities |
| UI container data exfiltration | UI ingress bridge disables IP masquerading; UI is not attached to model-egress; runtime egress probe | Host routing/firewall changes or alternate interfaces can alter the result |
| Model server egress | Only Ollama is attached to the model-egress network | Egress is not allowlisted by this Compose file; enforce policy at host/network layer |
| Container privilege escalation | Non-root UIDs, dropped capabilities, no-new-privileges, read-only root FS, PID/resource limits | Docker daemon is privileged; host kernel/container runtime remain trusted |
| Data loss | Named persistent volumes and documented backup/restore | Backups can be incomplete or untested |
| Supply-chain compromise | Version-pinned upstream bases; release requires digest lock, SBOM, provenance, and review | Upstream publisher compromise and unreviewed model artifacts |
| Malicious or unsafe model artifact | Model/license review and explicit pull workflow | Model behavior and licensing cannot be fully guaranteed |

## Security assumptions and limitations

- The host OS, Docker Engine, operator account, and firewall are trusted and patched.
- Both application processes run as fixed non-root UIDs: Ollama 10002 and Open WebUI 10001.
- Anyone with Docker daemon access is effectively privileged on the host.
- Model download requires outbound connectivity. The Ollama service has an egress-capable network; this kit does not implement a complete registry/model-source allowlist.
- Open WebUI is attached to the internal inference network and a separate bridge whose IP masquerading is disabled. The runtime smoke workflow tests direct outbound TCP connectivity from the UI container. This is not a substitute for host firewall policy.
- NVIDIA device access for the non-root Ollama UID may require supplementary group configuration on some hosts; GPU support is not claimed until tested.
- Do not expose the UI directly to the public Internet. Use a private VPN or an authenticated reverse proxy with TLS and network controls.
- This kit does not guarantee privacy, regulatory compliance, or safe model outputs.
