# IK-04 Offline Bundle Format

The connected staging process creates a directory containing:

| File | Purpose |
|---|---|
| `images.tar` | Locally exported Ollama, Qdrant, and RAG API container images |
| `models.tar.gz` | Ollama model volume contents, including manifests and blobs |
| `manifest.json` | Product/version, platform, image references, model names, artifact list, creation time |
| `SHA256SUMS` | Checksums for all bundle files |
| `compose.yaml` | Offline runtime topology; all images use `pull_policy: never` |
| `.env.example` | Non-secret deployment configuration |
| `install.sh` | Offline installer |
| `README.md` | Target-side instructions |

The installer verifies SHA-256 checksums before loading images or extracting models. It creates named volumes, restores the model archive, initializes Qdrant volume ownership, and starts the stack with `docker compose up --pull never`.

SHA-256 checksums do not authenticate the origin of a bundle. Transfer the bundle through a trusted channel and sign the manifest or full archive with an organizational signing key when authenticity is required. Never include secrets in the bundle.
