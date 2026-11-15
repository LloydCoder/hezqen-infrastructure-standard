#!/usr/bin/env python3
"""Validate the required HEZQEN product-manifest contract using stdlib only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be a JSON object"]
    required = {"schemaVersion", "id", "name", "version", "license", "description", "runtime"}
    missing = sorted(required - data.keys())
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
    allowed = required | {"repository", "documentation", "support", "maintainers"}
    extra = sorted(data.keys() - allowed)
    if extra:
        errors.append("unknown fields: " + ", ".join(extra))
    if data.get("schemaVersion") != "1.0.0":
        errors.append("schemaVersion must equal 1.0.0")
    if not isinstance(data.get("id"), str) or not SLUG.fullmatch(data["id"]):
        errors.append("id must be a lowercase kebab-case slug")
    for field in ("name", "license", "description"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    if isinstance(data.get("version"), str):
        if not SEMVER.fullmatch(data["version"]):
            errors.append("version must follow Semantic Versioning")
    else:
        errors.append("version must be a string")
    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime must be an object")
    else:
        if set(runtime) - {"networkRequired", "supportedPlatforms", "containerized"}:
            errors.append("runtime contains unknown fields")
        if not isinstance(runtime.get("networkRequired"), bool):
            errors.append("runtime.networkRequired must be a boolean")
        if "supportedPlatforms" in runtime:
            platforms = runtime["supportedPlatforms"]
            if not isinstance(platforms, list) or any(not isinstance(x, str) or not x for x in platforms):
                errors.append("runtime.supportedPlatforms must be an array of non-empty strings")
        if "containerized" in runtime and not isinstance(runtime["containerized"], bool):
            errors.append("runtime.containerized must be a boolean")
    for field in ("repository", "documentation", "support"):
        if field in data:
            value = data[field]
            parsed = urlparse(value) if isinstance(value, str) else None
            if not parsed or parsed.scheme not in {"https", "http"} or not parsed.netloc:
                errors.append(f"{field} must be an absolute HTTP(S) URL")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-manifest.py PATH", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read valid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {path} satisfies the HIES product manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
