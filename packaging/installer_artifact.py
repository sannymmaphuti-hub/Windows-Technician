"""Installer artifact build boundary for Windows Technician."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installation_package_validation import (
    validate_installation_package,
)
from packaging.installation_staging import stage_installation_package
from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class InstallerArtifactContract:
    """Canonical contract for the generated installer artifact."""

    application_name: str
    version: str
    artifact_name: str
    artifact_root: Path

    def __post_init__(self) -> None:
        if self.application_name != APPLICATION_METADATA.display_name:
            raise ValueError(
                "Installer application name must match application metadata."
            )

        if self.version != APPLICATION_METADATA.version:
            raise ValueError(
                "Installer version must match application metadata."
            )

        if not self.artifact_name.strip():
            raise ValueError("Installer artifact name cannot be empty.")

        if not isinstance(self.artifact_root, Path):
            raise TypeError("artifact_root must be a Path.")


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INSTALLER_ARTIFACT_CONTRACT = InstallerArtifactContract(
    application_name=INSTALLER_CONTRACT.application_name,
    version=INSTALLER_CONTRACT.version,
    artifact_name=f"WindowsTechnician-{APPLICATION_METADATA.version}-Setup",
    artifact_root=PROJECT_ROOT / "installer_artifacts",
)


@dataclass(frozen=True)
class InstallerArtifactResult:
    """Result of generating the installer artifact."""

    success: bool
    artifact: Path | None
    errors: tuple[str, ...] = ()


def build_installer_artifact() -> InstallerArtifactResult:
    """Build a deterministic installer package from validated staging."""

    staged = stage_installation_package()
    validation = validate_installation_package(staged)

    if not staged.success:
        return InstallerArtifactResult(
            success=False,
            artifact=None,
            errors=staged.errors,
        )

    if not validation.valid:
        return InstallerArtifactResult(
            success=False,
            artifact=None,
            errors=validation.errors,
        )

    artifact_root = INSTALLER_ARTIFACT_CONTRACT.artifact_root
    artifact_root.mkdir(parents=True, exist_ok=True)

    artifact = artifact_root / (
        INSTALLER_ARTIFACT_CONTRACT.artifact_name + ".zip"
    )

    if artifact.exists():
        artifact.unlink()

    archive_base = artifact.with_suffix("")

    if archive_base.exists():
        shutil.rmtree(archive_base)

    shutil.copytree(
        staged.staging_root,
        archive_base,
    )

    archive_created = shutil.make_archive(
        str(archive_base),
        "zip",
        root_dir=artifact_root,
        base_dir=archive_base.name,
    )

    generated_artifact = Path(archive_created)

    shutil.rmtree(archive_base)

    if not generated_artifact.exists():
        return InstallerArtifactResult(
            success=False,
            artifact=None,
            errors=(
                f"Installer artifact was not created: {generated_artifact}",
            ),
        )

    return InstallerArtifactResult(
        success=True,
        artifact=generated_artifact,
    )
