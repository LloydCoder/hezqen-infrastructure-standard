#!/usr/bin/env python3
"""Build, verify, and safely install an offline HEZQEN infrastructure bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

PRODUCTS = (
    "local-ai-deployment",
    "pii-protection",
    "multigpu-optimization",
    "airgapped-rag",
)
VERSION_RE = re.compile(r"^\\d+\\.\\d+\\.\\d+(?:[-+][0-9A-Za-z.-]+)?$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_archive_name(name: object) -> bool:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name or ":" in name:
        return False
    path = PurePosixPath(name)
    return (
        path.as_posix() == name
        and not path.is_absolute()
        and bool(path.parts)
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _product_version(product_dir: Path) -> tuple[str, str]:
    manifest = json.loads((product_dir / "product-manifest.json").read_text(encoding="utf-8"))
    product_id = manifest.get("id")
    version = manifest.get("version")
    if product_id not in PRODUCTS or not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise ValueError(f"invalid product identity or version in {product_dir}")
    return product_id, version


def build_bundle(root: Path, output_dir: Path, source_revision: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40,64}", source_revision):
        raise ValueError("source_revision must be a full lowercase Git commit SHA")
    root = root.resolve(strict=True)
    products_root = root / "products"
    output_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []

    for product_id in PRODUCTS:
        product_dir = products_root / product_id
        manifest_path = product_dir / "product-manifest.json"
        if not manifest_path.is_file():
            raise ValueError(f"required product manifest missing: {product_id}")
        product_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual_id, version = _product_version(product_dir)
        if actual_id != product_id:
            raise ValueError(f"product directory/manifest identity mismatch: {product_id}")
        archive_name = f"{product_id}-{version}.tar.gz"
        archive_path = output_dir / archive_name
        with tarfile.open(archive_path, "w:gz", compresslevel=9) as archive:
            for path in sorted(product_dir.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(product_dir)
                if any(part in {".git", ".venv", "__pycache__"} for part in relative.parts):
                    continue
                if path.name == ".env" or path.suffix in {".pyc", ".pyo"}:
                    continue
                archive.add(path, arcname=(PurePosixPath(product_id) / PurePosixPath(relative.as_posix())).as_posix(), recursive=False)
        entries.append({
            "id": product_id,
            "version": version,
            "license": product_manifest["license"],
            "archive": archive_name,
            "sha256": sha256_file(archive_path),
            "sizeBytes": archive_path.stat().st_size,
            "sourceRevision": source_revision,
            "documentation": product_manifest["documentation"],
            "supportedPlatforms": product_manifest["runtime"]["supportedPlatforms"],
        })
        components.append({
            "type": "application",
            "name": product_manifest["name"],
            "version": version,
            "licenses": [{"license": {"id": product_manifest["license"]}}],
            "purl": f"pkg:generic/hezqen/{product_id}@{version}",
            "properties": [{"name": "hezqen:sourceRevision", "value": source_revision}],
        })

    bundle_manifest = {
        "schemaVersion": "1.0.0",
        "name": "HEZQEN Infrastructure Lab Bundle",
        "version": "0.1.0",
        "sourceRevision": source_revision,
        "products": entries,
    }
    (output_dir / "bundle-manifest.json").write_text(
        json.dumps(bundle_manifest, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "HEZQEN Infrastructure Lab Bundle",
                "version": "0.1.0",
            },
            "properties": [{"name": "hezqen:sourceRevision", "value": source_revision}],
        },
        "components": components,
    }
    (output_dir / "sbom.cdx.json").write_text(
        json.dumps(sbom, indent=2, sort_keys=True) + "\\n", encoding="utf-8"
    )
    checksum_files = sorted(
        path for path in output_dir.iterdir()
        if path.is_file() and path.name not in {"SHA256SUMS"}
    )
    (output_dir / "SHA256SUMS").write_text(
        "".join(f"{sha256_file(path)}  {path.name}\\n" for path in checksum_files),
        encoding="utf-8",
    )
    return bundle_manifest


def verify_bundle(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = bundle_dir.resolve(strict=True)
        manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schemaVersion") != "1.0.0":
            errors.append("unsupported bundle schemaVersion")
        if not re.fullmatch(r"[0-9a-f]{40,64}", str(manifest.get("sourceRevision", ""))):
            errors.append("invalid bundle sourceRevision")
        products = manifest.get("products")
        if not isinstance(products, list):
            return errors + ["bundle products must be an array"]
        ids = [item.get("id") for item in products if isinstance(item, dict)]
        if len(ids) != len(PRODUCTS) or set(ids) != set(PRODUCTS):
            errors.append("bundle must contain each of the four required products exactly once")
        seen_archives: set[str] = set()
        for item in products:
            if not isinstance(item, dict):
                errors.append("invalid product entry")
                continue
            archive_name = item.get("archive")
            if not _safe_archive_name(archive_name) or len(PurePosixPath(str(archive_name)).parts) != 1:
                errors.append(f"unsafe archive path: {archive_name}")
                continue
            if archive_name in seen_archives:
                errors.append(f"duplicate archive path: {archive_name}")
                continue
            seen_archives.add(archive_name)
            archive_path = root / archive_name
            try:
                if archive_path.is_symlink() or not archive_path.is_file() or not archive_path.resolve().is_relative_to(root):
                    raise ValueError("archive missing, symlinked, or outside bundle directory")
                if sha256_file(archive_path) != item.get("sha256"):
                    errors.append(f"SHA-256 mismatch: {archive_name}")
                if archive_path.stat().st_size != item.get("sizeBytes"):
                    errors.append(f"size mismatch: {archive_name}")
                with tarfile.open(archive_path, "r:gz") as archive:
                    members = archive.getmembers()
                    for member in members:
                        if not _safe_archive_name(member.name):
                            raise ValueError(f"unsafe archive member: {member.name}")
                        if not (member.isfile() or member.isdir()):
                            raise ValueError(f"unsupported archive member type: {member.name}")
                        if not member.name.startswith(f"{item.get('id')}/"):
                            raise ValueError(f"archive member outside product root: {member.name}")
                    manifest_member = archive.extractfile(f"{item.get('id')}/product-manifest.json")
                    if manifest_member is None:
                        raise ValueError("product manifest missing from archive")
                    product_manifest = json.load(manifest_member)
                    if product_manifest.get("id") != item.get("id") or product_manifest.get("version") != item.get("version"):
                        raise ValueError("archived product identity/version does not match bundle manifest")
                    if product_manifest.get("license") != item.get("license"):
                        raise ValueError("archived product license does not match bundle manifest")
            except (OSError, tarfile.TarError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"cannot verify {archive_name}: {exc}")
        sums_path = root / "SHA256SUMS"
        if not sums_path.is_file() or sums_path.is_symlink():
            errors.append("SHA256SUMS missing or unsafe")
        else:
            try:
                expected_files: set[str] = set()
                for line in sums_path.read_text(encoding="utf-8").splitlines():
                    digest, separator, filename = line.partition("  ")
                    if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest) or not _safe_archive_name(filename) or len(PurePosixPath(filename).parts) != 1:
                        errors.append("invalid SHA256SUMS entry")
                        continue
                    if filename in expected_files:
                        errors.append(f"duplicate SHA256SUMS entry: {filename}")
                        continue
                    expected_files.add(filename)
                    candidate = root / filename
                    if candidate.is_symlink() or not candidate.is_file() or sha256_file(candidate) != digest:
                        errors.append(f"SHA256SUMS verification failed: {filename}")
                required_files = seen_archives | {"bundle-manifest.json", "sbom.cdx.json"}
                if expected_files != required_files:
                    errors.append("SHA256SUMS inventory does not match bundle contents")
            except OSError as exc:
                errors.append(f"cannot read SHA256SUMS: {exc}")
        sbom_path = root / "sbom.cdx.json"
        if not sbom_path.is_file() or sbom_path.is_symlink():
            errors.append("CycloneDX SBOM missing or unsafe")
        else:
            try:
                sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
                if sbom.get("bomFormat") != "CycloneDX" or sbom.get("specVersion") != "1.6":
                    errors.append("invalid CycloneDX SBOM metadata")
                if len(sbom.get("components", [])) != len(PRODUCTS):
                    errors.append("SBOM must contain all four product components")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"cannot read CycloneDX SBOM: {exc}")
    except (OSError, json.JSONDecodeError, TypeError, AttributeError) as exc:
        errors.append(f"cannot read bundle manifest: {exc}")
    return errors


def install_bundle(bundle_dir: Path, destination: Path) -> list[Path]:
    errors = verify_bundle(bundle_dir)
    if errors:
        raise ValueError("; ".join(errors))
    root = bundle_dir.resolve(strict=True)
    manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
    target_root = destination.resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    products_root = target_root / "products"
    products_root.mkdir(exist_ok=True)
    installed: list[Path] = []
    for item in manifest["products"]:
        product_id = item["id"]
        target = products_root / product_id
        if target.exists():
            raise FileExistsError(f"refusing to overwrite existing product: {target}")
        with tempfile.TemporaryDirectory(dir=target_root) as temporary:
            staging = Path(temporary)
            with tarfile.open(root / item["archive"], "r:gz") as archive:
                for member in archive.getmembers():
                    if not _safe_archive_name(member.name):
                        raise ValueError(f"unsafe archive member: {member.name}")
                    relative = PurePosixPath(member.name)
                    output = staging.joinpath(*relative.parts)
                    if member.isdir():
                        output.mkdir(parents=True, exist_ok=True)
                    elif member.isfile():
                        output.parent.mkdir(parents=True, exist_ok=True)
                        source = archive.extractfile(member)
                        if source is None:
                            raise ValueError(f"cannot read archive member: {member.name}")
                        with source, output.open("xb") as destination_file:
                            shutil.copyfileobj(source, destination_file)
                    else:
                        raise ValueError(f"unsupported archive member type: {member.name}")
            staged_product = staging / product_id
            if not staged_product.is_dir():
                raise ValueError(f"archive did not produce expected product directory: {product_id}")
            os.replace(staged_product, target)
        installed.append(target)
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--source-revision", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("bundle", type=Path)
    install = subparsers.add_parser("install")
    install.add_argument("bundle", type=Path)
    install.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        build_bundle(args.root, args.output, args.source_revision)
        print(f"OK: offline bundle built at {args.output}")
        return 0
    if args.command == "verify":
        errors = verify_bundle(args.bundle)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print("OK: offline bundle integrity verified")
        return 0
    install_bundle(args.bundle, args.destination)
    print(f"OK: four products installed at {args.destination / 'products'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
