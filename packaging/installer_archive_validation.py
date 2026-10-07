"""Validation boundary for the Windows Technician installer artifact."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.installer_artifact import (
    INSTALLER_ARTIFACT_CONTRACT,
)


@dataclass(frozen=True)
class InstallerArchiveValidationResult:
    """Result of validating an installer ZIP archive."""

    valid: bool
    artifact: Path
    file_count: int
    errors: tuple[str, ...] = ()


def validate_installer_archive(
    artifact: Path | None = None,
) -> InstallerArchiveValidationResult:
    """Validate the contents and safety of the installer archive."""

    archive = (
        Path(artifact)
        if artifact is not None
        else (
            INSTALLER_ARTIFACT_CONTRACT.artifact_root
            / f"{INSTALLER_ARTIFACT_CONTRACT.artifact_name}.zip"
        )
    )

    errors: list[str] = []

    if not archive.exists():
        return InstallerArchiveValidationResult(
            valid=False,
            artifact=archive,
            file_count=0,
            errors=(f"Installer archive does not exist: {archive}",),
        )

    if not archive.is_file():
        return InstallerArchiveValidationResult(
            valid=False,
            artifact=archive,
            file_count=0,
            errors=(f"Installer archive is not a file: {archive}",),
        )

    try:
        with ZipFile(archive, "r") as zip_file:
            members = zip_file.namelist()
    except Exception as exc:
        return InstallerArchiveValidationResult(
            valid=False,
            artifact=archive,
            file_count=0,
            errors=(f"Installer archive could not be opened: {exc}",),
        )

    if not members:
        errors.append("Installer archive is empty.")

    normalized_members = [
        member.replace("\\", "/")
        for member in members
    ]

    for member in normalized_members:
        parts = Path(member).parts

        if ".." in parts:
            errors.append(
                f"Installer archive contains a path traversal entry: {member}"
            )

    archive_root = INSTALLER_ARTIFACT_CONTRACT.artifact_name + "/"

    root_members = [
        member
        for member in normalized_members
        if member.startswith(archive_root)
    ]

    if not root_members:
        errors.append(
            f"Installer archive does not contain the expected artifact root: "
            f"{archive_root}"
        )

    executable_path = (
        archive_root
        + INSTALLER_CONTRACT.executable_name
    )

    if executable_path not in normalized_members:
        errors.append(
            "Installer archive does not contain the Windows Technician executable."
        )

    internal_prefix = archive_root + "_internal/"

    has_internal_runtime = any(
        member.startswith(internal_prefix)
        for member in normalized_members
    )

    if not has_internal_runtime:
        errors.append(
            "Installer archive does not contain the bundled runtime."
        )

    forbidden_fragments = (
        "/.git/",
        "/tests/",
        "/build/",
        "/installer_artifacts/",
        "/installer_staging/",
    )

    for member in normalized_members:
        if any(fragment in member for fragment in forbidden_fragments):
            errors.append(
                f"Installer archive contains forbidden project content: {member}"
            )

    return InstallerArchiveValidationResult(
        valid=not errors,
        artifact=archive,
        file_count=len(members),
        errors=tuple(errors),
    )

