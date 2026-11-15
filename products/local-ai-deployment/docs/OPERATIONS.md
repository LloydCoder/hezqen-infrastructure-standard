# IK-01 Operations Runbook

## Start and inspect

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=100
```

## Pull a model

```bash
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama list
```

Model pulls require outbound access. Review model provenance and license before use.

## Backup

Stop the stack for a consistent cold backup:

```bash
docker compose down
docker run --rm -v hezqen-local-ai_ollama_data:/source:ro -v "$PWD/backups:/backup" alpine:3.22 tar -czf /backup/ollama_data.tgz -C /source .
docker run --rm -v hezqen-local-ai_open_webui_data:/source:ro -v "$PWD/backups:/backup" alpine:3.22 tar -czf /backup/open_webui_data.tgz -C /source .
```

Verify archive checksums and store backups encrypted with access restricted to authorized operators. Confirm the actual volume names with `docker volume ls`; Compose project-name overrides may change the prefix.

## Restore

Stop the stack. Inspect backup archives before extraction. Restore into the corresponding named volumes using a trusted, pinned utility image and the documented volume names. Do not overwrite a live data volume. Start the stack and verify users, model inventory, and application health before reopening access.

## Upgrade and rollback

1. Read upstream release notes and security advisories.
2. Update image tags in `.env` only in a reviewed change.
3. Resolve and record immutable image digests for release candidates.
4. Back up both named volumes.
5. Pull images, recreate containers, and run health checks.
6. Test inference and UI authentication with a non-sensitive prompt.
7. If verification fails, restore the prior image digests and data backup where schema compatibility requires it.

Never use `latest` for a production deployment. Do not roll back an application image across a data migration without checking upstream compatibility.

## Uninstall

`docker compose down` removes containers and networks but retains named volumes. Data deletion is a separate destructive operation. Confirm the exact volume names and obtain explicit operator approval before running `docker compose down -v`.
