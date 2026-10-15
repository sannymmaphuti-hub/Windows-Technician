"""Fail-closed Authenticode verification for production release artifacts."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
def find_signtool(explicit_path: str | Path | None = None) -> Path | None:
    """Locate SignTool, preferring an explicitly configured executable."""
    if explicit_path is not None:
        candidate = Path(explicit_path)
        return candidate if candidate.is_file() else None
    located = shutil.which("signtool.exe") or shutil.which("signtool")
    if located:
        return Path(located)
    root = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Windows Kits" / "10" / "bin"
    candidates = list(root.glob("*/x64/signtool.exe"))
    return sorted(candidates, key=lambda path: path.parts[-3], reverse=True)[0] if candidates else None
def verify_authenticode_signature(artifact: str | Path, *, signtool_path: str | Path | None = None, runner: Callable = subprocess.run) -> bool:
    """Return True only when SignTool successfully verifies a trusted signature."""
    target = Path(artifact)
    if not target.is_file():
        return False
    tool = find_signtool(signtool_path)
    if tool is None:
        return False
    try:
        result = runner([str(tool), "verify", "/pa", "/all", "/v", str(target.resolve())], capture_output=True, text=True, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return getattr(result, "returncode", 1) == 0
def write_verified_release_manifest(artifact: str | Path, *, application_name: str, version: str, manifest_path: str | Path | None = None, signtool_path: str | Path | None = None, runner: Callable = subprocess.run) -> Path:
    """Write a verified manifest only after successful Authenticode verification."""
    target = Path(artifact).resolve()
    if not verify_authenticode_signature(target, signtool_path=signtool_path, runner=runner):
        raise RuntimeError("Authenticode verification failed; verified manifest was not created.")
    from packaging.release_build_pipeline import write_release_manifest
    destination = Path(manifest_path) if manifest_path is not None else target.with_suffix(".manifest.json")
    write_release_manifest(target, application_name=application_name, version=version, manifest_path=destination)
    data = json.loads(destination.read_text(encoding="utf-8"))
    data["integrity_only"] = False
    data["signature_verified"] = True
    data["signature_verification"] = {"method": "SignTool verify /pa /all /v", "verified_utc": datetime.now(timezone.utc).isoformat(), "tool": str(find_signtool(signtool_path))}
    destination.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return destination
