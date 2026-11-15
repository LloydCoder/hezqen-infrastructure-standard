import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "validate-workflows.py"
SPEC = importlib.util.spec_from_file_location("validate_workflows", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class WorkflowValidationTests(unittest.TestCase):
    def test_all_repository_workflows_parse_and_use_pinned_actions(self):
        self.assertEqual(MODULE.validate_tree(ROOT / ".github" / "workflows"), [])
        self.assertEqual(MODULE.validate_tree(ROOT / "workflows"), [])

    def test_rejects_unpinned_action(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.yml"
            path.write_text(
                "name: test\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - uses: actions/checkout@v4\n",
                encoding="utf-8",
            )
            errors = MODULE.validate_workflow(path)
            self.assertTrue(any("not pinned" in error for error in errors))

    def test_rejects_pull_request_target(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.yml"
            path.write_text(
                "name: test\non:\n  pull_request_target:\njobs:\n  build:\n    runs-on: ubuntu-latest\n",
                encoding="utf-8",
            )
            errors = MODULE.validate_workflow(path)
            self.assertTrue(any("pull_request_target" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
