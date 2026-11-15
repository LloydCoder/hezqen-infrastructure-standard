#!/usr/bin/env python3
"""Validate product workspaces and their minimum deployment security contracts."""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTATION = ("README.md", "THREAT_MODEL.md", "SECURITY.md", "CHANGELOG.md", "docs/OPERATIONS.md", "docs/COMPATIBILITY.md")


def validate_product(path: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads((path / "product-manifest.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors.extend(f"{path.name}: manifest {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in validator.iter_errors(manifest))
        if manifest.get("id") != path.name:
            errors.append(f"{path.name}: manifest id must match workspace directory")
        for relative in DOCUMENTATION:
            if not (path / relative).is_file():
                errors.append(f"{path.name}: required documentation missing: {relative}")
        runtime = manifest.get("runtime", {})
        if runtime.get("containerized") is False:
            if (path / "compose.yaml").exists():
                errors.append(f"{path.name}: non-containerized workspace must not declare compose.yaml")
            return errors
        compose_path = path / "compose.yaml"
        if not compose_path.is_file():
            errors.append(f"{path.name}: compose.yaml is required for containerized products")
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
            if any("/var/run/docker.sock" in str(mount) for mount in service.get("volumes", [])):
                errors.append(f"{path.name}: service {service_name} must not mount the Docker socket")
        if path.name == "local-ai-deployment":
            ollama, webui, networks = services.get("ollama", {}), services.get("open-webui", {}), compose.get("networks", {})
            if not ollama or not webui:
                errors.append("local-ai-deployment: ollama and open-webui services are required")
            if ollama.get("user") != "10002:10002" or webui.get("user") != "10001:10001":
                errors.append("local-ai-deployment: application containers must use their fixed non-root UIDs")
            for name, service in (("ollama", ollama), ("open-webui", webui)):
                dockerfile = service.get("build", {}).get("dockerfile")
                if not dockerfile or not (path / dockerfile).is_file():
                    errors.append(f"local-ai-deployment: {name} must use a checked-in derived Dockerfile")
                if "@sha256:" not in str(service.get("build", {}).get("args", {}).get("BASE_IMAGE", "")):
                    errors.append(f"local-ai-deployment: {name} base image must be digest-pinned")
            for script in ("scripts/backup.sh", "scripts/restore.sh"):
                if not (path / script).is_file():
                    errors.append(f"local-ai-deployment: required backup/restore script missing: {script}")
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
        if path.name == "airgapped-rag":
            ollama, qdrant, api = services.get("ollama", {}), services.get("qdrant", {}), services.get("rag-api", {})
            networks = compose.get("networks", {})
            if not ollama or not qdrant or not api:
                errors.append("airgapped-rag: ollama, qdrant, and rag-api services are required")
            if ollama.get("ports") or qdrant.get("ports"):
                errors.append("airgapped-rag: Ollama and Qdrant APIs must not publish host ports")
            api_ports = api.get("ports", [])
            if not api_ports or not all(str(p).startswith("${RAG_BIND_ADDRESS:-127.0.0.1}:") for p in api_ports):
                errors.append("airgapped-rag: RAG API must bind to host loopback by default")
            if networks.get("rag-backend", {}).get("driver_opts", {}).get("com.docker.network.bridge.enable_ip_masquerade") != "false":
                errors.append("airgapped-rag: backend network must disable IP masquerading")
            if "@sha256:" not in str(qdrant.get("image", "")):
                errors.append("airgapped-rag: Qdrant image must be digest-pinned")
            if any(service.get("pull_policy") != "never" for service in (ollama, qdrant, api)):
                errors.append("airgapped-rag: every service must use pull_policy=never on the offline target")
            for script in ("scripts/prepare-models.sh", "scripts/package-offline.sh", "scripts/install-offline.sh"):
                if not (path / script).is_file():
                    errors.append(f"airgapped-rag: required offline lifecycle script missing: {script}")
            if not (path / "images.lock.json").is_file():
                errors.append("airgapped-rag: images.lock.json is required")
            if not (path / "Dockerfile.api").is_file() or "@sha256:" not in (path / "Dockerfile.api").read_text(encoding="utf-8"):
                errors.append("airgapped-rag: API base image must be digest-pinned")
            ollama_dockerfile = ROOT / "products" / "local-ai-deployment" / "Dockerfile.ollama"
            if not ollama_dockerfile.is_file() or "@sha256:" not in ollama_dockerfile.read_text(encoding="utf-8"):
                errors.append("airgapped-rag: shared Ollama base image must be digest-pinned")
    except (OSError, json.JSONDecodeError, yaml.YAMLError, TypeError, AttributeError, ValueError) as exc:
        errors.append(f"{path.name}: unable to validate product workspace: {exc}")
    return errors



def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def validate_build_tools(root: Path = ROOT) -> list[str]:
    """Require exact product build-system pins to match the audited requirements file."""
    errors: list[str] = []
    requirements_path = root / "requirements-dev.txt"
    try:
        lines = requirements_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"unable to read audited development requirements: {exc}"]

    audited_pins: dict[str, str] = {}
    for line in lines:
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        name, separator, version = entry.partition("==")
        if separator and name and version:
            normalized = normalize_package_name(name)
            if normalized in audited_pins and audited_pins[normalized] != version:
                errors.append(f"requirements-dev.txt: conflicting pins for {name}")
            audited_pins[normalized] = version

    for pyproject in sorted((root / "products").glob("*/pyproject.toml")):
        try:
            config = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            requirements = config.get("build-system", {}).get("requires", [])
            if not isinstance(requirements, list):
                errors.append(f"{pyproject}: build-system.requires must be a list")
                continue
            for requirement in requirements:
                if not isinstance(requirement, str):
                    errors.append(f"{pyproject}: build-system requirements must be strings")
                    continue
                name, separator, version = requirement.partition("==")
                if not separator or not name or not version or any(char in version for char in "<>=!~;"):
                    errors.append(f"{pyproject}: build requirement must be pinned with ==: {requirement}")
                    continue
                normalized = normalize_package_name(name)
                if normalized not in audited_pins:
                    errors.append(f"{pyproject}: build requirement {requirement} must be mirrored in requirements-dev.txt")
                elif audited_pins[normalized] != version:
                    errors.append(
                        f"{pyproject}: build requirement {requirement} must match the audited requirements-dev pin {audited_pins[normalized]}"
                    )
        except (OSError, tomllib.TOMLDecodeError, AttributeError, TypeError) as exc:
            errors.append(f"{pyproject}: unable to validate build-system requirements: {exc}")
    return errors


def main() -> int:
    schema_path = ROOT / "schemas" / "product-manifest.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot load product schema: {exc}", file=sys.stderr)
        return 2
    product_root = ROOT / "products"
    workspaces = sorted(path for path in product_root.iterdir() if path.is_dir()) if product_root.exists() else []
    if not workspaces:
        print("ERROR: no product workspaces found", file=sys.stderr)
        return 1
    errors = validate_build_tools() + [error for workspace in workspaces for error in validate_product(workspace, schema)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: validated {len(workspaces)} product workspace(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
