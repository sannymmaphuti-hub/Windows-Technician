"""Tests for installation package validation."""

from pathlib import Path

from packaging.installation_package_validation import (
    InstallationPackageValidationResult,
    validate_installation_package,
)
from packaging.installation_staging import (
    InstallationStageResult,
    stage_installation_package,
)


def test_validation_result_is_immutable():
    result = InstallationPackageValidationResult(
        valid=True,
        staging_root=Path("stage"),
        executable=Path("stage") / "WindowsTechnician.exe",
        file_count=1,
    )

    try:
        result.valid = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "InstallationPackageValidationResult must be immutable."
        )


def test_staged_package_is_valid():
    staged = stage_installation_package()

    result = validate_installation_package(staged)

    assert result.valid is True
    assert result.errors == ()


def test_validation_returns_canonical_executable():
    staged = stage_installation_package()

    result = validate_installation_package(staged)

    assert result.executable is not None
    assert result.executable.name == "WindowsTechnician.exe"


def test_validation_counts_actual_files():
    staged = stage_installation_package()

    result = validate_installation_package(staged)

    assert result.file_count > 1
    assert result.file_count == staged.files_copied


def test_validation_requires_internal_runtime():
    staged = stage_installation_package()

    staged.staging_root.joinpath("_internal").rename(
        staged.staging_root / "_internal_backup"
    )

    result = validate_installation_package(staged)

    assert result.valid is False
    assert any(
        "Bundled runtime directory is missing" in error
        for error in result.errors
    )


def test_validation_rejects_invalid_result_type():
    try:
        validate_installation_package("invalid")  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Validation must reject an invalid staging result type."
        )
