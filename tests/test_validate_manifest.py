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
        self.assertIn("manifest root must be a JSON object", MODULE.validate([]))

    def test_rejects_missing_required_fields(self):
        errors = MODULE.validate({})
        self.assertTrue(any("missing required fields" in item for item in errors))

    def test_rejects_invalid_slug(self):
        data = self.valid_manifest()
        data["id"] = "Local AI"
        self.assertIn("id must be a lowercase kebab-case slug", MODULE.validate(data))

    def test_rejects_invalid_semver(self):
        data = self.valid_manifest()
        data["version"] = "v1"
        self.assertIn("version must follow Semantic Versioning", MODULE.validate(data))

    def test_rejects_unknown_top_level_fields(self):
        data = self.valid_manifest()
        data["unexpected"] = True
        self.assertTrue(any("unknown fields" in item for item in MODULE.validate(data)))

    def test_requires_boolean_network_policy(self):
        data = self.valid_manifest()
        data["runtime"]["networkRequired"] = "false"
        self.assertIn("runtime.networkRequired must be a boolean", MODULE.validate(data))

    def test_rejects_non_http_urls(self):
        data = self.valid_manifest()
        data["repository"] = "javascript:alert(1)"
        self.assertIn("repository must be an absolute HTTP(S) URL", MODULE.validate(data))


if __name__ == "__main__":
    unittest.main()
