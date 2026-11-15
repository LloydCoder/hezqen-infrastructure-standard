#!/usr/bin/env python3
"""Parse and enforce basic security invariants for HIES workflow YAML."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

PINNED_ACTION = re.compile(r"^[^@]+@[0-9a-f]{40}$")


def walk_steps(value: Any):
    if isinstance(value, dict):
        if isinstance(value.get("uses"), str):
            yield value["uses"]
        for child in value.values():
            yield from walk_steps(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_steps(child)


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
        document = yaml.safe_load(raw)
    except (OSError, yaml.YAMLError) as exc:
        return [f"{path}: invalid YAML: {exc}"]
    if not isinstance(document, dict):
        return [f"{path}: workflow document must be a mapping"]
    if not isinstance(document.get("name"), str) or not document["name"].strip():
        errors.append(f"{path}: workflow name is required")
    jobs = document.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        errors.append(f"{path}: at least one job is required")
    if "pull_request_target" in raw:
        errors.append(f"{path}: pull_request_target is prohibited by the HIES workflow baseline")
    if "write-all" in raw:
        errors.append(f"{path}: write-all token permissions are prohibited")
    for reference in walk_steps(document):
        if not PINNED_ACTION.fullmatch(reference):
            errors.append(f"{path}: action reference is not pinned to a full commit SHA: {reference}")
    return errors


def validate_tree(root: Path) -> list[str]:
    errors: list[str] = []
    candidates = sorted(root.rglob("*.yml")) + sorted(root.rglob("*.yaml"))
    candidates = [path for path in candidates if ".git" not in path.parts]
    for path in candidates:
        errors.extend(validate_workflow(path))
    if not candidates:
        errors.append(f"{root}: no YAML workflow/configuration files found")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--roots",
        nargs="+",
        type=Path,
        default=[Path(".github/workflows"), Path("workflows")],
    )
    args = parser.parse_args()
    errors = []
    for root in args.roots:
        if root.exists():
            errors.extend(validate_tree(root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: workflow YAML parses and all third-party actions use immutable SHA references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
