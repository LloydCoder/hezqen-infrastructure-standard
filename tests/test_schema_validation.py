import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate-schemas.py"
SPEC = importlib.util.spec_from_file_location("validate_schemas", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SchemaValidationTests(unittest.TestCase):
    def test_all_schemas_and_fixtures_validate(self):
        root = Path(__file__).parents[1]
        self.assertEqual(
            MODULE.validate_samples(root / "schemas", root / "tests" / "fixtures"),
            [],
        )

    def test_invalid_manifest_fixture_is_rejected_by_schema(self):
        root = Path(__file__).parents[1]
        schema, registry = MODULE.load_registry(root / "schemas")
        manifest_schema = next(
            item for item in schema if item["$id"].endswith("/product-manifest.schema.json")
        )
        from jsonschema import Draft202012Validator, FormatChecker
        document = MODULE.load_json(root / "tests" / "fixtures" / "product-manifest.invalid.json")
        validator = Draft202012Validator(
            manifest_schema, registry=registry, format_checker=FormatChecker()
        )
        self.assertTrue(list(validator.iter_errors(document)))


if __name__ == "__main__":
    unittest.main()
