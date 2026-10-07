"""Tests for the production Windows build boundary."""

from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA
from packaging.package_manifest import PRODUCTION_PACKAGE_MANIFEST
from packaging.production_build import (
    PRODUCTION_BUILD_CONTRACT,
    BuildValidationResult,
    build_executable_path,
    validate_build_artifact,
    validate_build_inputs,
)


def test_build_contract_matches_application_metadata():
    assert (
        PRODUCTION_BUILD_CONTRACT.application_name
        == APPLICATION_METADATA.display_name
    )
    assert (
        PRODUCTION_BUILD_CONTRACT.version
        == APPLICATION_METADATA.version
    )
    assert (
        PRODUCTION_BUILD_CONTRACT.executable_name
        == APPLICATION_METADATA.executable_name
    )


def test_build_contract_matches_package_manifest():
    assert (
        PRODUCTION_BUILD_CONTRACT.entry_point
        == PRODUCTION_PACKAGE_MANIFEST.entry_point
    )


def test_build_contract_uses_canonical_paths():
    assert isinstance(PRODUCTION_BUILD_CONTRACT.project_root, Path)
    assert isinstance(PRODUCTION_BUILD_CONTRACT.build_root, Path)
    assert isinstance(PRODUCTION_BUILD_CONTRACT.distribution_root, Path)


def test_build_executable_path_uses_onedir_layout():
    path = build_executable_path()

    assert path.name == "WindowsTechnician.exe"
    assert path.parent.name == "WindowsTechnician"
    assert path.parent == (
        PRODUCTION_BUILD_CONTRACT.distribution_root
        / "WindowsTechnician"
    )


def test_build_inputs_are_valid():
    result = validate_build_inputs()

    assert isinstance(result, BuildValidationResult)
    assert result.valid is True
    assert result.errors == ()


def test_existing_onedir_artifact_is_valid():
    result = validate_build_artifact()

    assert result.valid is True
    assert result.errors == ()


def test_build_validation_result_is_immutable():
    result = BuildValidationResult(valid=True)

    try:
        result.valid = False
    except AttributeError:
        pass
    else:
        raise AssertionError("BuildValidationResult must be immutable.")
