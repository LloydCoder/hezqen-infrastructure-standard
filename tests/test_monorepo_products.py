"""Regression tests for monorepo product boundaries and IK-01 security defaults."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products" / "local-ai-deployment"
RUNTIME_WORKFLOW = ROOT / ".github" / "workflows" / "ik01-runtime.yml"


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
        self.assertEqual(compose["services"]["open-webui"]["expose"], ["8080"])

    def test_open_webui_listens_on_container_interface(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        self.assertEqual(compose["services"]["open-webui"]["environment"]["HOST"], "0.0.0.0")
        self.assertEqual(compose["services"]["open-webui"]["environment"]["HOME"], "/tmp")

    def test_ui_network_has_no_ip_masquerading(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        networks = compose["networks"]
        services = compose["services"]
        self.assertTrue(networks["inference"]["internal"])
        self.assertEqual(
            networks["ui-ingress"]["driver_opts"]["com.docker.network.bridge.enable_ip_masquerade"],
            "false",
        )
        self.assertEqual(services["open-webui"]["networks"], ["ui-ingress", "inference"])
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

    def test_open_webui_uses_a_non_root_build(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        service = compose["services"]["open-webui"]
        dockerfile = (PRODUCT / "Dockerfile.open-webui").read_text(encoding="utf-8")
        self.assertEqual(service["user"], "10001:10001")
        self.assertEqual(service["build"]["dockerfile"], "Dockerfile.open-webui")
        self.assertIn("adduser --uid 10001", dockerfile)
        self.assertIn("USER 10001:10001", dockerfile)
        self.assertIn("chown -R 10001:10001 /app/backend/data", dockerfile)

    def test_ollama_uses_a_non_root_build(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        service = compose["services"]["ollama"]
        dockerfile = (PRODUCT / "Dockerfile.ollama").read_text(encoding="utf-8")
        self.assertEqual(service["user"], "10002:10002")
        self.assertEqual(service["build"]["dockerfile"], "Dockerfile.ollama")
        self.assertIn("ollama:x:10002:10002", dockerfile)
        self.assertIn("USER 10002:10002", dockerfile)
        self.assertIn("chown -R 10002:10002 /home/ollama", dockerfile)

    def test_base_images_are_pinned_by_digest(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        lock = json.loads((PRODUCT / "images.lock.json").read_text(encoding="utf-8"))
        self.assertEqual(
            lock["images"]["ollama"]["digest"],
            compose["services"]["ollama"]["build"]["args"]["BASE_IMAGE"].split("@")[-1].rstrip("}"),
        )
        self.assertEqual(
            lock["images"]["openWebUI"]["digest"],
            compose["services"]["open-webui"]["build"]["args"]["BASE_IMAGE"].split("@")[-1].rstrip("}"),
        )

    def test_build_context_excludes_operator_secrets(self) -> None:
        dockerignore = (PRODUCT / ".dockerignore").read_text(encoding="utf-8")
        self.assertIn(".env", dockerignore)
        self.assertIn(".env.*", dockerignore)
        self.assertIn("backups/", dockerignore)

    def test_backup_restore_scripts_require_integrity_and_confirmation(self) -> None:
        backup = (PRODUCT / "scripts" / "backup.sh").read_text(encoding="utf-8")
        restore = (PRODUCT / "scripts" / "restore.sh").read_text(encoding="utf-8")
        self.assertIn("sha256sum", backup)
        self.assertIn("sha256sum -c", restore)
        self.assertIn("--confirm", restore)
        self.assertIn("tarfile.open", restore)
        self.assertIn("PurePosixPath", restore)
        self.assertIn("member.issym()", restore)
        self.assertIn("member.islnk()", restore)
        self.assertIn("--network none", backup)
        self.assertIn("--network none", restore)

    def test_default_cpu_limits_are_portable_to_two_core_hosts(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        self.assertEqual(compose["services"]["ollama"]["cpus"], "${OLLAMA_CPUS:-2.0}")
        self.assertEqual(compose["services"]["open-webui"]["cpus"], "${WEBUI_CPUS:-1.0}")

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

    def test_embedding_model_is_routed_to_ollama(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.yaml").read_text(encoding="utf-8"))
        env = compose["services"]["open-webui"]["environment"]
        self.assertEqual(env["RAG_EMBEDDING_ENGINE"], "ollama")
        self.assertEqual(env["RAG_EMBEDDING_MODEL"], "nomic-embed-text")

    def test_nvidia_override_is_opt_in_and_scoped_to_ollama(self) -> None:
        compose = yaml.safe_load((PRODUCT / "compose.nvidia.yaml").read_text(encoding="utf-8"))
        self.assertEqual(list(compose["services"]), ["ollama"])
        devices = compose["services"]["ollama"]["deploy"]["resources"]["reservations"]["devices"]
        self.assertEqual(devices[0]["driver"], "nvidia")
        self.assertIn("gpu", devices[0]["capabilities"])

    def test_runtime_workflow_builds_non_root_images_before_start(self) -> None:
        workflow = yaml.safe_load(RUNTIME_WORKFLOW.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["cpu-runtime"]["steps"]
        names = [step["name"] for step in steps]
        self.assertLess(
            names.index("Build non-root product images"),
            names.index("Start stack and wait for health"),
        )
        self.assertIn("Verify Open WebUI and Ollama run as non-root", names)
        self.assertIn("Verify CPU model inference and embedding", names)
        self.assertIn("Run backup and restore drill", names)
        self.assertIn("Validate IK-01 shell scripts", names)

    def test_runtime_workflow_creates_secret_before_compose_validation(self) -> None:
        workflow = yaml.safe_load(RUNTIME_WORKFLOW.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["cpu-runtime"]["steps"]
        names = [step["name"] for step in steps]
        self.assertLess(
            names.index("Create ephemeral test secret"),
            names.index("Validate base and NVIDIA Compose configurations"),
        )
        self.assertLess(
            names.index("Verify host port publication and UI health"),
            names.index("Verify UI-to-inference connectivity"),
        )

    def test_product_has_required_operational_and_security_docs(self) -> None:
        for relative in ("THREAT_MODEL.md", "SECURITY.md", "CHANGELOG.md", "docs/OPERATIONS.md", "docs/COMPATIBILITY.md"):
            with self.subTest(file=relative):
                self.assertTrue((PRODUCT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
