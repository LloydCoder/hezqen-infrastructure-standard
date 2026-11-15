from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.bundle import build_bundle, install_bundle, verify_bundle  # noqa: E402


class BundleTests(unittest.TestCase):
    def test_build_verify_and_install_all_four_products(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            destination = Path(temporary) / "installed"
            manifest = build_bundle(ROOT, output, "a" * 40)
            self.assertEqual(
                {item["id"] for item in manifest["products"]},
                {"local-ai-deployment", "pii-protection", "multigpu-optimization", "airgapped-rag"},
            )
            self.assertEqual(verify_bundle(output), [])
            installed = install_bundle(output, destination)
            self.assertEqual(len(installed), 4)
            self.assertTrue((destination / "products" / "airgapped-rag" / "compose.yaml").is_file())
            self.assertTrue((destination / "products" / "local-ai-deployment" / "product-manifest.json").is_file())

    def test_verification_rejects_tampered_product_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            build_bundle(ROOT, output, "b" * 40)
            archive = next(output.glob("*.tar.gz"))
            archive.write_bytes(archive.read_bytes() + b"tamper")
            errors = verify_bundle(output)
            self.assertTrue(any("SHA-256 mismatch" in error for error in errors))

    def test_install_rejects_path_traversal_in_archive_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            build_bundle(ROOT, output, "c" * 40)
            manifest_path = output / "bundle-manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["products"][0]["archive"] = "../escape.tar.gz"
            manifest_path.write_text(json.dumps(manifest))
            errors = verify_bundle(output)
            self.assertTrue(any("unsafe archive path" in error for error in errors))

    def test_manifest_binds_bundle_to_source_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            manifest = build_bundle(ROOT, output, "d" * 40)
            self.assertEqual(manifest["sourceRevision"], "d" * 40)
            self.assertEqual(manifest["schemaVersion"], "1.0.0")
            self.assertTrue((output / "sbom.cdx.json").is_file())


if __name__ == "__main__":
    unittest.main()
