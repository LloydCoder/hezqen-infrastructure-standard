from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products" / "pii-protection"
sys.path.insert(0, str(PRODUCT / "src"))

from hezqen_pii import Detection, PiiPolicyViolation, RedactionEngine, RedactionError  # noqa: E402


class BrokenDetector:
    def detect(self, text: str) -> list[Detection]:
        raise RuntimeError("simulated recognizer failure")


class InvalidSpanDetector:
    def detect(self, text: str) -> list[Detection]:
        return [Detection("EMAIL", 0, 3, 0.9, "bad")]


class PiiProtectionTests(unittest.TestCase):
    def test_redacts_email_and_luhn_valid_payment_card(self) -> None:
        result = RedactionEngine().redact("Contact a.person@example.com; card 4111 1111 1111 1111")
        self.assertNotIn("a.person@example.com", result)
        self.assertNotIn("4111 1111 1111 1111", result)
        self.assertIn("[EMAIL_1]", result)
        self.assertIn("[CREDIT_CARD_2]", result)

    def test_invalid_luhn_card_is_not_redacted(self) -> None:
        self.assertEqual(RedactionEngine().redact("Card 4111 1111 1111 1112"), "Card 4111 1111 1111 1112")

    def test_nested_json_values_are_redacted(self) -> None:
        result = RedactionEngine().redact_json({"user": {"email": "a@example.com"}, "items": ["call +1 212-555-0100"]})
        self.assertNotIn("a@example.com", str(result))
        self.assertNotIn("+1 212-555-0100", str(result))

    def test_block_policy_rejects_detected_pii(self) -> None:
        with self.assertRaises(PiiPolicyViolation):
            RedactionEngine(action="block").redact("a@example.com")

    def test_detector_failure_fails_closed(self) -> None:
        with self.assertRaisesRegex(RedactionError, "payload withheld"):
            RedactionEngine([BrokenDetector()]).redact("a@example.com")

    def test_invalid_detector_span_fails_closed(self) -> None:
        with self.assertRaises(RedactionError):
            RedactionEngine([InvalidSpanDetector()]).redact("a@example.com")

    def test_entity_allowlist_limits_detection(self) -> None:
        result = RedactionEngine(entities={"EMAIL"}).redact("a@example.com 192.0.2.10")
        self.assertIn("[EMAIL_1]", result)
        self.assertIn("192.0.2.10", result)

    def test_hmac_pseudonymization_is_deterministic(self) -> None:
        engine = RedactionEngine(action="pseudonymize", hmac_key=b"test-secret-key")
        self.assertEqual(engine.redact("a@example.com"), engine.redact("a@example.com"))
        self.assertNotIn("a@example.com", engine.redact("a@example.com"))

    def test_pseudonymization_requires_a_key(self) -> None:
        with self.assertRaises(ValueError):
            RedactionEngine(action="pseudonymize")

    def test_unsupported_json_values_are_rejected(self) -> None:
        with self.assertRaises(RedactionError):
            RedactionEngine().redact_json({"value": object()})

    def test_runtime_workflow_exercises_pii_api_security_contract(self) -> None:
        import yaml
        workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "ik02-runtime.yml").read_text(encoding="utf-8"))
        steps = workflow["jobs"]["runtime"]["steps"]
        names = [step["name"] for step in steps]
        self.assertIn("Verify non-root identity and loopback host binding", names)
        self.assertIn("Verify PII redaction and no request-body logging", names)
        self.assertIn("Verify block policy fails closed", names)
        self.assertIn("Verify PII service has no direct Internet egress", names)

    def test_pii_product_manifest_and_compose_contract(self) -> None:
        import json
        import yaml
        manifest = json.loads((PRODUCT / "product-manifest.json").read_text(encoding="utf-8"))
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        service = compose["services"]["pii-protection"]
        self.assertEqual(manifest["id"], PRODUCT.name)
        dockerfile = (PRODUCT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY --chown=10001:10001 src/ /app/", dockerfile)
        self.assertEqual(service["user"], "10001:10001")
        self.assertTrue(service["read_only"])
        self.assertEqual(service["cap_drop"], ["ALL"])
        self.assertIn("no-new-privileges:true", service["security_opt"])
        self.assertTrue(service["ports"][0].startswith("${PII_BIND_ADDRESS:-127.0.0.1}:"))
        self.assertEqual(compose["networks"]["pii"]["driver_opts"]["com.docker.network.bridge.enable_ip_masquerade"], "false")


if __name__ == "__main__":
    unittest.main()
