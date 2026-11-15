#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: verify-checksums.sh CHECKSUM_FILE ARTIFACT" >&2
  exit 2
fi

checksum_file=$1
artifact=$2

[ -f "$checksum_file" ] || { echo "checksum file not found" >&2; exit 2; }
[ -f "$artifact" ] || { echo "artifact not found" >&2; exit 2; }

if command -v sha256sum >/dev/null 2>&1; then
  expected=$(awk 'NR == 1 { print $1 }' "$checksum_file" | tr 'A-F' 'a-f')
  actual=$(sha256sum "$artifact" | awk '{ print $1 }')
elif command -v shasum >/dev/null 2>&1; then
  expected=$(awk 'NR == 1 { print $1 }' "$checksum_file")
  actual=$(shasum -a 256 "$artifact" | awk '{ print $1 }')
else
  echo "neither sha256sum nor shasum is available" >&2
  exit 2
fi

case "$expected" in
  *[!0-9a-fA-F]*|'') echo "invalid SHA-256 checksum format" >&2; exit 2 ;;
esac
[ "${#expected}" -eq 64 ] || { echo "checksum must contain 64 hexadecimal characters" >&2; exit 2; }

if [ "$expected" != "$actual" ]; then
  echo "CHECKSUM MISMATCH: $artifact" >&2
  exit 1
fi

echo "OK: SHA-256 verified for $artifact"
