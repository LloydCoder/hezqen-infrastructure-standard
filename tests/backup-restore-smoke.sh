#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
PRODUCT="$ROOT/products/local-ai-deployment"
HELPER_IMAGE="hezqen/ollama:0.40.16-nonroot"
TEMP_DIR="$(mktemp -d)"
SUFFIX="$$"
OLLAMA_TEST_VOLUME="hezqen-ik01-backup-test-ollama-$SUFFIX"
WEBUI_TEST_VOLUME="hezqen-ik01-backup-test-webui-$SUFFIX"
BACKUP_DIR="$TEMP_DIR/backup"

cleanup() {
  docker volume rm "$OLLAMA_TEST_VOLUME" "$WEBUI_TEST_VOLUME" >/dev/null 2>&1 || true
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

docker image inspect "$HELPER_IMAGE" >/dev/null
docker volume create "$OLLAMA_TEST_VOLUME" >/dev/null
docker volume create "$WEBUI_TEST_VOLUME" >/dev/null

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$OLLAMA_TEST_VOLUME,dst=/data" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'mkdir -p /data/models && printf "ollama-volume-original\n" > /data/models/backup-smoke.txt && chown -R 10002:10002 /data'

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$WEBUI_TEST_VOLUME,dst=/data" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'mkdir -p /data/uploads && printf "webui-volume-original\n" > /data/uploads/backup-smoke.txt && chown -R 10001:10001 /data'

OLLAMA_VOLUME="$OLLAMA_TEST_VOLUME" WEBUI_VOLUME="$WEBUI_TEST_VOLUME" BACKUP_HELPER_IMAGE="$HELPER_IMAGE" \
  "$PRODUCT/scripts/backup.sh" "$BACKUP_DIR"

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$OLLAMA_TEST_VOLUME,dst=/data" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'printf "mutated\n" > /data/models/backup-smoke.txt'

docker run --rm --network none --user 0:0 \
  --mount "type=volume,src=$WEBUI_TEST_VOLUME,dst=/data" \
  --entrypoint /bin/sh "$HELPER_IMAGE" -euc \
  'printf "mutated\n" > /data/uploads/backup-smoke.txt'

OLLAMA_VOLUME="$OLLAMA_TEST_VOLUME" WEBUI_VOLUME="$WEBUI_TEST_VOLUME" BACKUP_HELPER_IMAGE="$HELPER_IMAGE" \
  "$PRODUCT/scripts/restore.sh" "$BACKUP_DIR" --confirm

OLLAMA_RESTORED="$(docker run --rm --network none --user 0:0 --mount "type=volume,src=$OLLAMA_TEST_VOLUME,dst=/data,readonly" --entrypoint /bin/sh "$HELPER_IMAGE" -euc 'cat /data/models/backup-smoke.txt')"
WEBUI_RESTORED="$(docker run --rm --network none --user 0:0 --mount "type=volume,src=$WEBUI_TEST_VOLUME,dst=/data,readonly" --entrypoint /bin/sh "$HELPER_IMAGE" -euc 'cat /data/uploads/backup-smoke.txt')"

test "$OLLAMA_RESTORED" = "ollama-volume-original"
test "$WEBUI_RESTORED" = "webui-volume-original"
echo "IK-01 backup/restore smoke passed; original data and volume contents were restored."
