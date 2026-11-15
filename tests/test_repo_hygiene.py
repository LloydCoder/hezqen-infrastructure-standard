import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check-repo-hygiene.py"
SPEC = importlib.util.spec_from_file_location("repo_hygiene", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class RepositoryHygieneTests(unittest.TestCase):
    def test_clean_repository_has_no_findings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("Public documentation only.", encoding="utf-8")
            self.assertEqual(MODULE.scan(root), [])

    def test_detects_private_key_header(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "leak.txt").write_text("-----BEGIN " + "PRIVATE KEY-----", encoding="utf-8")
            self.assertTrue(any("private-key header" in item for item in MODULE.scan(root)))

    def test_detects_aws_access_key_pattern(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            token = "AKIA" + "A" * 16
            (root / "config.txt").write_text(token, encoding="utf-8")
            self.assertTrue(any("AWS access-key identifier" in item for item in MODULE.scan(root)))


if __name__ == "__main__":
    unittest.main()
