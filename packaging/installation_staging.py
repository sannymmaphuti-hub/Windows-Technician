"""Deterministic staging boundary for the Windows Technician installer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.production_build import build_executable_path


@dataclass(frozen=True)
class InstallationStageResult:
    """Result of staging the validated application package."""

    success: bool
    staging_root: Path
    executable: Path | None
    files_copied: int
    errors: tuple[str, ...] = ()


def default_staging_root() -> Path:
    """Return the canonical temporary installer staging directory."""

    return (
        Path(__file__).resolve().parent.parent
        / "installer_staging"
        / INSTALLER_CONTRACT.install_directory_name
    )


def stage_installation_package(
    *,
    staging_root: Path | None = None,
) -> InstallationStageResult:
    """Stage the validated PyInstaller application for installation."""

    source_root = build_executable_path().parent
    destination_root = Path(staging_root) if staging_root is not None else default_staging_root()

    errors: list[str] = []

    if not source_root.exists():
        return InstallationStageResult(
            success=False,
            staging_root=destination_root,
            executable=None,
            files_copied=0,
            errors=(f"Build output directory does not exist: {source_root}",),
        )

    if not source_root.is_dir():
        return InstallationStageResult(
            success=False,
            staging_root=destination_root,
            executable=None,
            files_copied=0,
            errors=(f"Build output path is not a directory: {source_root}",),
        )

    source_executable = build_executable_path()

    if not source_executable.exists():
        return InstallationStageResult(
            success=False,
            staging_root=destination_root,
            executable=None,
            files_copied=0,
            errors=(f"Build executable does not exist: {source_executable}",),
        )

    if destination_root.exists():
        shutil.rmtree(destination_root)

    destination_root.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(source_root, destination_root)

    staged_executable = destination_root / INSTALLER_CONTRACT.executable_name

    if not staged_executable.exists():
        errors.append(
            f"Staged executable does not exist: {staged_executable}"
        )

    files_copied = sum(
        1
        for path in destination_root.rglob("*")
        if path.is_file()
    )

    return InstallationStageResult(
        success=not errors,
        staging_root=destination_root,
        executable=staged_executable if staged_executable.exists() else None,
        files_copied=files_copied,
        errors=tuple(errors),
    )
