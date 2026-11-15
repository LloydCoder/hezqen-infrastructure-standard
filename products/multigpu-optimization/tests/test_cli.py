from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class PlannerCliTests(unittest.TestCase):
    def test_cli_emits_machine_readable_plan(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable, "-m", "hezqen_gpu_planner",
                "--model", "org/example-70b",
                "--params-b", "70", "--layers", "80", "--kv-heads", "8", "--head-dim", "128",
                "--model-context", "32768", "--context", "8192", "--concurrency", "8",
                "--gpus-per-node", "4", "--nodes", "1", "--vram-gib", "24", "--tp", "4",
                "--pp", "1", "--weight-dtype", "int4", "--quantization", "awq",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["model"]["name"], "org/example-70b")
        self.assertIn("--tensor-parallel-size 4", payload["vllm"]["shell_command"])

    def test_cli_returns_nonzero_when_fail_if_no_fit_is_requested(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable, "-m", "hezqen_gpu_planner",
                "--model", "org/example-70b",
                "--params-b", "70", "--layers", "80", "--kv-heads", "8", "--head-dim", "128",
                "--model-context", "32768", "--context", "8192", "--concurrency", "8",
                "--gpus-per-node", "4", "--nodes", "1", "--vram-gib", "8", "--tp", "4",
                "--pp", "1", "--weight-dtype", "int4", "--quantization", "awq", "--fail-if-no-fit",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertTrue(json.loads(result.stdout)["memory"]["estimated_fit"] is False)


if __name__ == "__main__":
    unittest.main()
