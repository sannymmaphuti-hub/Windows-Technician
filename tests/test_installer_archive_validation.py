"""Tests for installer archive validation."""

from pathlib import Path
from zipfile import ZipFile

from packaging.installer_archive_validation import (
    InstallerArchiveValidationResult,
    validate_installer_archive,
)
from packaging.installer_artifact import build_installer_artifact


def test_archive_validation_result_is_immutable():
    result = InstallerArchiveValidationResult(
        valid=True,
        artifact=Path("installer.zip"),
        file_count=1,
    )

    try:
        result.valid = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "InstallerArchiveValidationResult must be immutable."
        )


def test_generated_installer_archive_is_valid():
    artifact = build_installer_artifact()

    result = validate_installer_archive(artifact.artifact)

    assert result.valid is True
    assert result.errors == ()


def test_archive_contains_files():
    artifact = build_installer_artifact()

    result = validate_installer_archive(artifact.artifact)

    assert result.file_count > 1


def test_archive_contains_windows_executable():
    artifact = build_installer_artifact()

    result = validate_installer_archive(artifact.artifact)

    with ZipFile(artifact.artifact, "r") as archive:
        names = archive.namelist()

    assert any(
        name.endswith("/WindowsTechnician.exe")
        for name in names
    )


def test_archive_contains_internal_runtime():
    artifact = build_installer_artifact()

    result = validate_installer_archive(artifact.artifact)

    with ZipFile(artifact.artifact, "r") as archive:
        names = archive.namelist()

    assert any(
        "/_internal/" in name
        for name in names
    )


def test_archive_rejects_path_traversal():
    artifact = build_installer_artifact()

    with ZipFile(artifact.artifact, "a") as archive:
        archive.writestr(
            "Windows Technician/../../escape.txt",
            "invalid",
        )

    result = validate_installer_archive(artifact.artifact)

    assert result.valid is False
    assert any(
        "path traversal" in error
        for error in result.errors
    )


def test_missing_archive_is_invalid(tmp_path):
    missing = tmp_path / "missing.zip"

    result = validate_installer_archive(missing)

    assert result.valid is False
    assert result.file_count == 0
