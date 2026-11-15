#!/usr/bin/env python3
"""Validate a HEZQEN product manifest against the normative JSON Schema."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


def validate(data: object, schema_path: Path | None = None) -> list[str]:
    path = schema_path or Path(__file__).parents[1] / "schemas" / "product-manifest.schema.json"
    try:
        schema: Any = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: (list(error.absolute_path), error.message),
        )
    except (OSError, json.JSONDecodeError, SchemaError, ValueError) as exc:
        return [f"schema validation could not run: {exc}"]
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in errors
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to product-manifest JSON")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parents[1] / "schemas" / "product-manifest.schema.json",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate(data, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.manifest} satisfies the HIES product manifest schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
