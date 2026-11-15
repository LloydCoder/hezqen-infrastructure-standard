#!/usr/bin/env python3
"""Validate HIES schemas and sample documents against JSON Schema Draft 2020-12."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_registry(schema_dir: Path) -> tuple[list[dict[str, Any]], Registry]:
    schemas: list[dict[str, Any]] = []
    registry = Registry()
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        schemas.append(schema)
        schema_id = schema.get("$id")
        if schema_id:
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return schemas, registry


def validate_samples(schema_dir: Path, fixtures_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        schemas, registry = load_registry(schema_dir)
    except (OSError, json.JSONDecodeError, SchemaError, ValueError) as exc:
        return [f"schema loading/validation failed: {exc}"]

    schema_by_name = {Path(schema["$id"]).name: schema for schema in schemas if "$id" in schema}
    for fixture in sorted(fixtures_dir.glob("*.json")):
        schema_name = fixture.name.split(".", 1)[0] + ".schema.json"
        schema = schema_by_name.get(schema_name)
        if schema is None:
            errors.append(f"{fixture}: no matching schema {schema_name}")
            continue
        try:
            document = load_json(fixture)
            validator = Draft202012Validator(
                schema, registry=registry, format_checker=FormatChecker()
            )
            validation_errors = sorted(
                validator.iter_errors(document),
                key=lambda error: (list(error.absolute_path), error.message),
            )
            if fixture.name.endswith(".invalid.json"):
                if not validation_errors:
                    errors.append(f"{fixture}: invalid fixture unexpectedly passed")
            elif validation_errors:
                errors.extend(
                    f"{fixture}: {'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
                    for error in validation_errors
                )
        except (OSError, json.JSONDecodeError, SchemaError, ValueError) as exc:
            errors.append(f"{fixture}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-dir", type=Path, default=Path("schemas"))
    parser.add_argument("--fixtures-dir", type=Path, default=Path("tests/fixtures"))
    args = parser.parse_args()

    try:
        schemas, _ = load_registry(args.schema_dir)
    except (OSError, json.JSONDecodeError, SchemaError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not schemas:
        print("ERROR: no *.schema.json files found", file=sys.stderr)
        return 1

    errors = validate_samples(args.schema_dir, args.fixtures_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(schemas)} Draft 2020-12 schemas and sample fixtures validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
