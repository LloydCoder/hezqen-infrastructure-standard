# IK-01 Operations Runbook

## Start and stop

From this directory:

```bash
docker compose config --quiet
docker compose build --pull
docker compose up -d --no-build
docker compose ps
docker compose logs -f --tail=100
docker compose down
```

Named volumes are retained by `docker compose down`. Do not add `-v` unless intentionally deleting all model and application data.

## Model lifecycle

Pull models explicitly through the Ollama service:

```bash
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama list
```

Review model provenance, license, and resource requirements before use. Model weights are stored in the `ollama_data` named volume.

## Backup

Build the product images before using the backup helper:

```bash
docker compose build --pull
mkdir -p backups
bash scripts/backup.sh "backups/hezqen-ik01-$(date -u +%Y%m%dT%H%M%SZ)"
```

The script:
- Resolves the Compose project's Ollama and Open WebUI named volumes.
- Stops the stack only if it is running, then restarts it after the backup.
- Creates numeric-owner-preserving compressed archives for both volumes.
- Writes SHA-256 checksum files and a JSON backup manifest.
- Uses the derived Ollama image as a local helper with `--network none`; no separate backup utility image is downloaded.

Backups contain model weights, prompts, conversations, uploaded files, and application state. They do not include `.env`, Compose configuration, host firewall settings, or Docker images. Back up configuration separately and keep secrets in an appropriate secret manager.

## Restore

Restore is destructive to the selected target volumes and requires an explicit confirmation flag:

```bash
bash scripts/restore.sh "backups/hezqen-ik01-YYYYMMDDTHHMMSSZ" --confirm
```

The script verifies checksums, validates archive paths against absolute paths and traversal entries, restores numeric ownership, and restarts the stack only if it was running before restore. To restore into a different Compose project, set both `OLLAMA_VOLUME` and `WEBUI_VOLUME` to the target volume names.

## Backup security and retention

The archives are not encrypted by these scripts. Store them on encrypted storage or encrypt them before transfer/off-site retention. Restrict directory permissions, define a retention policy, keep at least one off-site copy, and periodically perform a restore drill. Treat backups as sensitive data because they contain user prompts, documents, conversations, and model files.

## Updates and rollback

1. Review upstream release notes and security advisories.
2. Update the pinned base-image digests in `images.lock.json`, Compose defaults, Dockerfiles, and `.env.example` together.
3. Run schema validation, unit tests, and the full CPU runtime workflow.
4. Create a backup before upgrading.
5. Build the new derived images and start the stack.
6. Verify health, authentication, model availability, and application data.
7. If validation fails, stop the stack, restore the pre-upgrade backup, and rebuild the previously pinned image versions.

Never use `latest` tags. Do not update the lock file without matching runtime evidence.

## Resource management

Default CPU and memory limits are conservative starting values and can be adjusted in `.env`. Model memory requirements vary by architecture, quantization, context length, and concurrency. Monitor host memory, disk, and temperature during model pulls and inference.

## GPU

The optional `compose.nvidia.yaml` override is not yet acceptance-tested. Validate driver, NVIDIA Container Toolkit, device permissions for UID 10002, and model inference on the target hardware before relying on GPU acceleration.
