"""Controlled Windows Technician production release-build pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ReleaseBuildConfig:
    source_root: Path
    output_root: Path
    application_name: str = "WindowsTechnician"
    version: str = "1.0.0"
    one_file: bool = False

    def __post_init__(self):
        if not self.application_name.strip():
            raise ValueError("application_name is required.")
        if not self.version.strip():
            raise ValueError("version is required.")
        if not self.source_root.is_dir():
            raise ValueError("source_root must be an existing directory.")
        if not (self.source_root / "main.py").is_file():
            raise ValueError("source_root must contain main.py.")
        if not isinstance(self.one_file, bool):
            raise ValueError("one_file must be a boolean.")

    @property
    def executable_name(self) -> str:
        return f"{self.application_name}.exe"

    @property
    def entry_point(self) -> Path:
        return self.source_root / "main.py"


def build_command(
    config: ReleaseBuildConfig,
    *,
    python_executable: str = sys.executable,
) -> list[str]:
    """Construct a deterministic PyInstaller command without executing it."""
    build_root = config.source_root / "build" / "production_release"
    command = [
        python_executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        config.application_name,
        "--distpath",
        str(config.output_root),
        "--workpath",
        str(build_root / "work"),
        "--specpath",
        str(build_root / "spec"),
        "--paths",
        str(config.source_root),
    ]

    if config.one_file:
        command.append("--onefile")
    else:
        command.append("--onedir")

    resources = config.source_root / "resources"
    if resources.is_dir():
        # PyInstaller uses ';' as the Windows source/destination separator.
        command.extend(["--add-data", f"{resources};resources"])

    icon = resources / "windows_technician.ico"
    if icon.is_file():
        command.extend(["--icon", str(icon)])

    command.append(str(config.entry_point))
    return command


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_release_manifest(
    artifact: Path,
    *,
    application_name: str,
    version: str,
    manifest_path: Path | None = None,
) -> Path:
    """Write integrity metadata for an existing build artifact."""
    artifact = artifact.resolve()
    if not artifact.is_file():
        raise FileNotFoundError(f"Release artifact does not exist: {artifact}")

    destination = manifest_path or artifact.with_suffix(".manifest.json")
    destination.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "1.0",
        "application": application_name,
        "version": version,
        "artifact": artifact.name,
        "size_bytes": artifact.stat().st_size,
        "sha256": sha256_file(artifact),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "integrity_only": True,
        "signature_verified": False,
    }

    destination.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def build_release(
    config: ReleaseBuildConfig,
    *,
    python_executable: str = sys.executable,
    runner=subprocess.run,
) -> Path:
    """Build the executable and produce a SHA-256 release manifest."""
    if os.name != "nt":
        raise RuntimeError("Production Windows executable builds must run on Windows.")

    config.output_root.mkdir(parents=True, exist_ok=True)
    command = build_command(config, python_executable=python_executable)

    try:
        result = runner(
            command,
            cwd=str(config.source_root.parent),
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "PyInstaller is unavailable. Install the pinned build dependencies "
            "before creating a release."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"PyInstaller failed with exit code {result.returncode}."
        )

    artifact_root = (
        config.output_root
        if config.one_file
        else config.output_root / config.application_name
    )
    artifact = artifact_root / config.executable_name

    if not artifact.is_file():
        raise RuntimeError(
            f"Build reported success, but the expected artifact is missing: {artifact}"
        )

    write_release_manifest(
        artifact,
        application_name=config.application_name,
        version=config.version,
    )
    return artifact



def finalize_signed_release(artifact: str | Path, *, application_name: str, version: str, manifest_path: str | Path | None = None, signtool_path: str | Path | None = None, runner=subprocess.run) -> Path:
 """Finalize a candidate only after trusted Authenticode verification."""
 from packaging.authenticode_verification import write_verified_release_manifest
 return write_verified_release_manifest(artifact, application_name=application_name, version=version, manifest_path=manifest_path, signtool_path=signtool_path, runner=runner)
