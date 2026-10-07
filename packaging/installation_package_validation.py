"""Validation boundary for the staged Windows Technician installation package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.installation_staging import InstallationStageResult


@dataclass(frozen=True)
class InstallationPackageValidationResult:
    """Result of validating an installer staging tree."""

    valid: bool
    staging_root: Path
    executable: Path | None
    file_count: int
    errors: tuple[str, ...] = ()


def validate_installation_package(
    result: InstallationStageResult,
) -> InstallationPackageValidationResult:
    """Validate the structural integrity of an installation staging tree."""

    errors: list[str] = []

    if not isinstance(result, InstallationStageResult):
        raise TypeError("result must be an InstallationStageResult.")

    staging_root = result.staging_root

    if not staging_root.exists():
        errors.append(f"Staging root does not exist: {staging_root}")
        return InstallationPackageValidationResult(
            valid=False,
            staging_root=staging_root,
            executable=None,
            file_count=0,
            errors=tuple(errors),
        )

    if not staging_root.is_dir():
        errors.append(f"Staging root is not a directory: {staging_root}")
        return InstallationPackageValidationResult(
            valid=False,
            staging_root=staging_root,
            executable=None,
            file_count=0,
            errors=tuple(errors),
        )

    executable = staging_root / INSTALLER_CONTRACT.executable_name
    internal_root = staging_root / "_internal"

    if not executable.exists():
        errors.append(f"Installer executable is missing: {executable}")
    elif not executable.is_file():
        errors.append(f"Installer executable is not a file: {executable}")

    if not internal_root.exists():
        errors.append(f"Bundled runtime directory is missing: {internal_root}")
    elif not internal_root.is_dir():
        errors.append(f"Bundled runtime path is not a directory: {internal_root}")

    try:
        executable.relative_to(staging_root)
    except ValueError:
        errors.append("Installer executable escapes the staging root.")

    file_count = sum(
        1
        for path in staging_root.rglob("*")
        if path.is_file()
    )

    if file_count == 0:
        errors.append("Installation package contains no files.")

    if result.files_copied != file_count:
        errors.append(
            "Staging file count does not match the actual package file count."
        )

    return InstallationPackageValidationResult(
        valid=not errors,
        staging_root=staging_root,
        executable=executable if executable.is_file() else None,
        file_count=file_count,
        errors=tuple(errors),
    )
