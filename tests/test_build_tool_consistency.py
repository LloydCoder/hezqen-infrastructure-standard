from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_monorepo", ROOT / "scripts" / "validate-monorepo.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load monorepo validator for tests")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
validate_build_tools = VALIDATOR.validate_build_tools


class BuildToolConsistencyTests(unittest.TestCase):
    def write_fixture(self, root: Path, requirement: str, audited_requirement: str = "setuptools==84.2.1") -> None:
        (root / "requirements-dev.txt").write_text(
            f"pip-audit==2.10.1\n{requirement}\n",
            encoding="utf-8",
        )
        product = root / "products" / "sample"
        product.mkdir(parents=True)
        (product / "pyproject.toml").write_text(
            "[build-system]\n"
            f"requires = [\"{requirement}\"]\n"
            "build-backend = \"setuptools.build_meta\"\n",
            encoding="utf-8",
        )

    def test_build_backend_pin_must_be_mirrored_in_audited_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_fixture(root, "setuptools==84.2.1")
            self.assertEqual(validate_build_tools(root), [])

    def test_build_backend_version_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_fixture(root, "setuptools==75.8.0", "setuptools==84.2.1")
            errors = validate_build_tools(root)
            self.assertTrue(any("must match the audited requirements-dev pin" in error for error in errors))

    def test_unpinned_build_backend_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_fixture(root, "setuptools>=78.1.1", "setuptools==84.2.1")
            errors = validate_build_tools(root)
            self.assertTrue(any("must be pinned with ==" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
