#!/usr/bin/env python3
"""Create deterministic SHA-256 release metadata for a directory of artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_manifest(
    product: str, version: str, source_revision: str, artifact_dir: Path, output: Path | None = None
) -> dict:
    root = artifact_dir.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("artifact directory must be a directory")
    output_resolved = output.resolve() if output else None
    artifacts = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in release artifacts: {path}")
        if not path.is_file():
            continue
        if output_resolved and path.resolve() == output_resolved:
            continue
        relative = path.relative_to(root).as_posix()
        media_type, _ = mimetypes.guess_type(path.name)
        artifacts.append({
            "name": relative,
            "sha256": sha256_file(path),
            "mediaType": media_type or "application/octet-stream",
            "sizeBytes": path.stat().st_size,
        })
    if not artifacts:
        raise ValueError("artifact directory contains no regular files")
    return {
        "product": product,
        "version": version,
        "sourceRevision": source_revision,
        "artifacts": artifacts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = create_manifest(
            args.product, args.version, args.source_revision, args.artifact_dir, args.output
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Created release manifest: {args.output} ({len(manifest['artifacts'])} artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
