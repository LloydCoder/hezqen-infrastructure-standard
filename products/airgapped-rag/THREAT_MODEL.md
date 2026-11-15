# IK-04 Threat Model

## Assets
- Source documents, extracted chunks, embeddings, and Qdrant payloads.
- Ollama model artifacts and local inference requests.
- Offline deployment images, model archive, manifest, and checksums.
- Host integrity and Docker daemon control.

## Trust boundaries
- Connected staging machine to offline transfer media.
- Offline bundle to target host installer.
- Host loopback API to RAG API container.
- RAG API to Ollama and Qdrant over the private Docker bridge.
- Retrieved document content to the language model prompt.
- Container volumes to host filesystem.

## Threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Offline bundle tampering | SHA-256 manifest and strict checksum verification before loading | Checksums detect accidental/malicious changes only if manifest itself is obtained through a trusted channel; sign bundle externally for stronger authenticity |
| Registry/model network dependency on target | Images and model artifacts exported in advance; installer uses local load and Compose `--pull never` | Staging phase still needs a connected machine |
| Data/model exfiltration | No-masquerade Docker bridge, loopback API, no published Ollama/Qdrant ports, runtime egress probe | Host routing, IPv6, firewall, or privileged Docker access can change the boundary |
| Unauthorized API access | Host loopback binding | No built-in authentication; remote use requires a gateway/VPN |
| Vector database exposure | Qdrant has no published host ports and is only on the private bridge | Other containers/host Docker control remain trusted |
| Container privilege escalation | Non-root UIDs, read-only filesystems, dropped capabilities, no-new-privileges | Host kernel and Docker daemon remain trusted |
| Prompt injection in retrieved documents | System prompt treats retrieved context as untrusted and asks model to ignore embedded instructions | Prompt injection cannot be fully eliminated; review outputs and isolate tools/actions |
| Malicious or malformed document | Input size/count/metadata limits and JSON validation | File parsing/OCR are not included; only caller-supplied text is accepted |
| Data loss | Persistent named volumes and documented backup guidance | Restore drills and off-host encrypted backups remain operator responsibilities |

## Security assumptions
- The target host and Docker Engine are trusted, patched, and access-controlled.
- The offline bundle is transferred through an approved channel and its manifest/checksums are verified.
- The API remains local to the host unless protected by a separately configured authenticated gateway.
- Operators review model licenses, provenance, and security advisories before staging.
- The RAG API processes text supplied by callers; it does not parse PDFs, Office files, images, or archives.

## Residual risks
The default deployment is single-host and single-user. It does not provide tenant isolation, authentication, authorization, encryption at rest, document malware scanning, OCR, semantic access controls, or a complete prompt-injection defense. The language model may produce incorrect or unsupported content.
