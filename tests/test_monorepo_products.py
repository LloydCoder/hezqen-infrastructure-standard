"""Regression tests for monorepo product boundaries and IK-01 security defaults."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products" / "local-ai-deployment"


class MonorepoProductTests(unittest.TestCase):
    def test_product_manifest_identity_matches_workspace(self) -> None:
        manifest = json.loads((PRODUCT / "product-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["id"], PRODUCT.name)
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["runtime"]["supportedPlatforms"], ["linux/amd64"])

    def test_ollama_api_is_not_published_to_host(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("ports", compose["services"]["ollama"])

    def test_web_ui_binds_to_loopback_by_default(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        ports = compose["services"]["open-webui"]["ports"]
        self.assertEqual(ports, ["${WEBUI_BIND_ADDRESS:-127.0.0.1}:${WEBUI_PORT:-3000}:8080"])

    def test_ui_has_no_egress_network(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        networks = compose["networks"]
        services = compose["services"]
        self.assertTrue(networks["inference"]["internal"])
        self.assertEqual(services["open-webui"]["networks"], ["inference"])
        self.assertEqual(set(services["ollama"]["networks"]), {"inference", "model-egress"})

    def test_services_have_container_hardening(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        for service in compose["services"].values():
            with self.subTest(service=service.get("image")):
                self.assertTrue(service["read_only"])
                self.assertIn("ALL", service["cap_drop"])
                self.assertIn("no-new-privileges:true", service["security_opt"])
                self.assertIn("healthcheck", service)
                self.assertNotIn("/var/run/docker.sock", str(service.get("volumes", [])))

    def test_ui_waits_for_healthy_inference_service(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        dependency = compose["services"]["open-webui"]["depends_on"]["ollama"]
        self.assertEqual(dependency["condition"], "service_healthy")

    def test_ui_tracking_flags_are_explicitly_disabled(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        env = compose["services"]["open-webui"]["environment"]
        self.assertEqual(env["SCARF_NO_ANALYTICS"], "true")
        self.assertEqual(env["DO_NOT_TRACK"], "true")
        self.assertEqual(env["ANONYMIZED_TELEMETRY"], "false")

    def test_nvidia_override_is_opt_in_and_scoped_to_ollama(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.nvidia.yaml").read_text(encoding="utf-8"))
        self.assertEqual(list(compose["services"]), ["ollama"])
        devices = compose["services"]["ollama"]["deploy"]["resources"]["reservations"]["devices"]
        self.assertEqual(devices[0]["driver"], "nvidia")
        self.assertIn("gpu", devices[0]["capabilities"])

    def test_product_has_required_operational_and_security_docs(self) -> None:
        for relative in ("THREAT_MODEL.md", "SECURITY.md", "CHANGELOG.md", "docs/OPERATIONS.md", "docs/COMPATIBILITY.md"):
            with self.subTest(file=relative):
                self.assertTrue((PRODUCT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
