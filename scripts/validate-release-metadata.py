#!/usr/bin/env python3
"""Validate release metadata and verify every referenced artifact checksum."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(data: object, schema_path: Path) -> list[str]:
    try:
        schema: Any = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: (list(error.absolute_path), error.message),
        )
        return [
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        ]
    except (OSError, json.JSONDecodeError, SchemaError, ValueError) as exc:
        return [f"schema validation could not run: {exc}"]


def verify_artifacts(data: object, artifact_root: Path) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("artifacts"), list):
        return ["manifest artifacts must be an array"]
    root = artifact_root.resolve(strict=True)
    errors: list[str] = []
    seen: set[str] = set()
    for item in data["artifacts"]:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            errors.append("each artifact must have a string name")
            continue
        name = item["name"]
        relative = PurePosixPath(name)
        if (
            "\\" in name
            or "\x00" in name
            or ":" in name
            or relative.as_posix() != name
            or relative.is_absolute()
            or not relative.parts
            or any(part in {"", ".", ".."} for part in relative.parts)
        ):
            errors.append(f"unsafe artifact path: {name}")
            continue
        if name in seen:
            errors.append(f"duplicate artifact path: {name}")
            continue
        seen.add(name)
        candidate = root
        try:
            for part in relative.parts:
                candidate = candidate / part
                if candidate.is_symlink():
                    raise ValueError("symlink path component")
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError("path escapes artifact root or is not a regular file")
            actual = sha256_file(resolved)
            if actual != item.get("sha256"):
                errors.append(f"SHA-256 mismatch: {name}")
            if "sizeBytes" in item and resolved.stat().st_size != item["sizeBytes"]:
                errors.append(f"size mismatch: {name}")
        except (OSError, ValueError) as exc:
            errors.append(f"cannot verify {name}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parents[1] / "schemas" / "artifact-manifest.schema.json",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    errors = validate_manifest(data, args.schema)
    if args.artifact_root:
        try:
            errors.extend(verify_artifacts(data, args.artifact_root))
        except (OSError, ValueError) as exc:
            errors.append(f"cannot access artifact root: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: release metadata is valid" + (" and artifact checksums match" if args.artifact_root else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
