#!/usr/bin/env python3
"""Validate product workspaces and their minimum deployment security contracts."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def validate_product(path: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads((path / "product-manifest.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors.extend(
            f"{path.name}: manifest {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in validator.iter_errors(manifest)
        )
        if manifest.get("id") != path.name:
            errors.append(f"{path.name}: manifest id must match workspace directory")
        compose_path = path / "compose.yaml"
        if not compose_path.is_file():
            errors.append(f"{path.name}: compose.yaml is required")
            return errors
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        services = compose.get("services", {})
        if not isinstance(services, dict) or not services:
            errors.append(f"{path.name}: compose.yaml must define services")
            return errors
        for service_name, service in services.items():
            if not isinstance(service, dict):
                errors.append(f"{path.name}: service {service_name} must be a mapping")
                continue
            image = str(service.get("image", ""))
            if not image or ":latest" in image or image.endswith(":latest"):
                errors.append(f"{path.name}: service {service_name} must use an explicit non-latest image")
            user = str(service.get("user", ""))
            if not user or user in {"0", "0:0", "root"}:
                errors.append(f"{path.name}: service {service_name} must declare a non-root runtime user")
            if service.get("privileged") is True:
                errors.append(f"{path.name}: service {service_name} must not be privileged")
            if "ALL" not in service.get("cap_drop", []):
                errors.append(f"{path.name}: service {service_name} must drop all Linux capabilities")
            if "no-new-privileges:true" not in service.get("security_opt", []):
                errors.append(f"{path.name}: service {service_name} must set no-new-privileges")
            if not service.get("read_only", False):
                errors.append(f"{path.name}: service {service_name} must use a read-only root filesystem")
            if not service.get("healthcheck"):
                errors.append(f"{path.name}: service {service_name} must define a healthcheck")
            mounts = service.get("volumes", [])
            if any("/var/run/docker.sock" in str(mount) for mount in mounts):
                errors.append(f"{path.name}: service {service_name} must not mount the Docker socket")
        if path.name == "local-ai-deployment":
            ollama = services.get("ollama", {})
            webui = services.get("open-webui", {})
            networks = compose.get("networks", {})
            if not ollama or not webui:
                errors.append("local-ai-deployment: ollama and open-webui services are required")
            if ollama.get("user") != "10002:10002":
                errors.append("local-ai-deployment: Ollama must run as UID/GID 10002")
            if webui.get("user") != "10001:10001":
                errors.append("local-ai-deployment: Open WebUI must run as UID/GID 10001")
            for service_name, service in (("ollama", ollama), ("open-webui", webui)):
                build = service.get("build", {})
                dockerfile = build.get("dockerfile")
                if not dockerfile or not (path / dockerfile).is_file():
                    errors.append(f"local-ai-deployment: {service_name} must use a checked-in derived Dockerfile")
                base_image = str(build.get("args", {}).get("BASE_IMAGE", ""))
                if "@sha256:" not in base_image:
                    errors.append(f"local-ai-deployment: {service_name} base image must be digest-pinned")
            if ollama.get("ports"):
                errors.append("local-ai-deployment: Ollama API must not publish a host port")
            ports = webui.get("ports", [])
            if not ports or not all(str(p).startswith("${WEBUI_BIND_ADDRESS:-127.0.0.1}:") for p in ports):
                errors.append("local-ai-deployment: Open WebUI must bind to loopback by default")
            if webui.get("depends_on", {}).get("ollama", {}).get("condition") != "service_healthy":
                errors.append("local-ai-deployment: Open WebUI must wait for healthy Ollama")
            if networks.get("inference", {}).get("internal") is not True:
                errors.append("local-ai-deployment: inference network must be internal-only")
            if webui.get("networks") != ["ui-ingress", "inference"]:
                errors.append("local-ai-deployment: Open WebUI must attach only to UI ingress and internal inference networks")
            if networks.get("ui-ingress", {}).get("driver_opts", {}).get("com.docker.network.bridge.enable_ip_masquerade") != "false":
                errors.append("local-ai-deployment: UI ingress network must disable IP masquerading")
            if set(ollama.get("networks", [])) != {"inference", "model-egress"}:
                errors.append("local-ai-deployment: Ollama must attach to inference and model-egress networks")
    except (OSError, json.JSONDecodeError, yaml.YAMLError, TypeError, AttributeError, ValueError) as exc:
        errors.append(f"{path.name}: unable to validate product workspace: {exc}")
    return errors


def main() -> int:
    schema_path = ROOT / "schemas" / "product-manifest.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001 - validation boundary
        print(f"ERROR: cannot load product schema: {exc}", file=sys.stderr)
        return 2
    product_root = ROOT / "products"
    workspaces = sorted(path for path in product_root.iterdir() if path.is_dir()) if product_root.exists() else []
    if not workspaces:
        print("ERROR: no product workspaces found", file=sys.stderr)
        return 1
    errors = [error for workspace in workspaces for error in validate_product(workspace, schema)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(workspaces)} product workspace(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
