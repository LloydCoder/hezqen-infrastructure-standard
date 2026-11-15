import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate-manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ManifestValidationTests(unittest.TestCase):
    def valid_manifest(self):
        return {
            "schemaVersion": "1.0.0",
            "id": "local-ai-kit",
            "name": "Local AI Kit",
            "version": "1.2.3",
            "license": "Apache-2.0",
            "description": "A test manifest.",
            "runtime": {"networkRequired": False, "supportedPlatforms": ["linux/amd64"]},
        }

    def test_accepts_valid_manifest(self):
        self.assertEqual(MODULE.validate(self.valid_manifest()), [])

    def test_rejects_non_object_root(self):
        self.assertTrue(MODULE.validate([]))

    def test_rejects_missing_required_fields(self):
        errors = MODULE.validate({})
        self.assertTrue(any("required property" in item for item in errors))

    def test_rejects_invalid_slug(self):
        data = self.valid_manifest()
        data["id"] = "Local AI"
        self.assertTrue(MODULE.validate(data))

    def test_rejects_invalid_semver(self):
        data = self.valid_manifest()
        data["version"] = "v1"
        self.assertTrue(MODULE.validate(data))

    def test_rejects_unknown_top_level_fields(self):
        data = self.valid_manifest()
        data["unexpected"] = True
        self.assertTrue(any("Additional properties are not allowed" in item for item in MODULE.validate(data)))

    def test_requires_boolean_network_policy(self):
        data = self.valid_manifest()
        data["runtime"]["networkRequired"] = "false"
        self.assertTrue(MODULE.validate(data))

    def test_rejects_non_uri_urls(self):
        data = self.valid_manifest()
        data["repository"] = "not a uri"
        self.assertTrue(MODULE.validate(data))


if __name__ == "__main__":
    unittest.main()
