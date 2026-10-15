"""Tests for the Windows Technician installer artifact."""

from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installer_artifact import (
    INSTALLER_ARTIFACT_CONTRACT,
    InstallerArtifactResult,
    build_installer_artifact,
)


def test_installer_artifact_contract_matches_metadata():
    assert (
        INSTALLER_ARTIFACT_CONTRACT.application_name
        == APPLICATION_METADATA.display_name
    )
    assert (
        INSTALLER_ARTIFACT_CONTRACT.version
        == APPLICATION_METADATA.version
    )


def test_installer_artifact_contract_uses_zip():
    assert INSTALLER_ARTIFACT_CONTRACT.artifact_name.endswith(
        f"-{APPLICATION_METADATA.version}-Setup"
    )


def test_installer_artifact_contract_uses_path():
    assert isinstance(
        INSTALLER_ARTIFACT_CONTRACT.artifact_root,
        Path,
    )


def test_installer_artifact_result_is_immutable():
    result = InstallerArtifactResult(
        success=True,
        artifact=Path("installer.zip"),
    )

    try:
        result.success = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "InstallerArtifactResult must be immutable."
        )


def test_installer_artifact_builds_successfully():
    result = build_installer_artifact()

    assert result.success is True
    assert result.artifact is not None
    assert result.artifact.is_file()


def test_installer_artifact_has_zip_extension():
    result = build_installer_artifact()

    assert result.artifact is not None
    assert result.artifact.suffix == ".zip"


def test_installer_artifact_has_expected_name():
    result = build_installer_artifact()

    assert result.artifact is not None
    assert (
        result.artifact.name
        == "WindowsTechnician-1.0.0-Setup.zip"
    )
