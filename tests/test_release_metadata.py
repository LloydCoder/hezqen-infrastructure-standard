import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


CREATE = load_module("create_release_metadata", ROOT / "scripts" / "create-release-metadata.py")
VERIFY = load_module("validate_release_metadata", ROOT / "scripts" / "validate-release-metadata.py")


class ReleaseMetadataTests(unittest.TestCase):
    def test_generates_and_verifies_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifacts = root / "dist"
            artifacts.mkdir()
            (artifacts / "package.tar.gz").write_bytes(b"release payload")
            manifest = CREATE.create_manifest("sample-kit", "1.0.0", "1234567abcdef", artifacts)
            schema = ROOT / "schemas" / "artifact-manifest.schema.json"
            self.assertEqual(VERIFY.validate_manifest(manifest, schema), [])
            self.assertEqual(VERIFY.verify_artifacts(manifest, artifacts), [])

    def test_detects_tampered_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifacts = root / "dist"
            artifacts.mkdir()
            target = artifacts / "package.tar.gz"
            target.write_bytes(b"original")
            manifest = CREATE.create_manifest("sample-kit", "1.0.0", "1234567abcdef", artifacts)
            target.write_bytes(b"tampered")
            self.assertIn("SHA-256 mismatch: package.tar.gz", VERIFY.verify_artifacts(manifest, artifacts))

    def test_rejects_symlink_in_release_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifacts = root / "dist"
            artifacts.mkdir()
            target = root / "secret.txt"
            target.write_text("not part of release", encoding="utf-8")
            (artifacts / "link.txt").symlink_to(target)
            with self.assertRaises(ValueError):
                CREATE.create_manifest("sample-kit", "1.0.0", "1234567abcdef", artifacts)

    def test_rejects_path_traversal_in_manifest(self):
        data = {"artifacts": [{"name": "../secret", "sha256": "0" * 64}]}
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(VERIFY.verify_artifacts(data, Path(temp)))


if __name__ == "__main__":
    unittest.main()
