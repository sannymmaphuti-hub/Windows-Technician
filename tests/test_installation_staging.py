"""Tests for installer package staging."""

from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.installation_staging import (
    InstallationStageResult,
    default_staging_root,
    stage_installation_package,
)


def test_staging_result_is_immutable():
    result = InstallationStageResult(
        success=True,
        staging_root=Path("stage"),
        executable=Path("stage") / "WindowsTechnician.exe",
        files_copied=1,
    )

    try:
        result.success = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "InstallationStageResult must be immutable."
        )


def test_default_staging_root_uses_installer_contract():
    path = default_staging_root()

    assert path.name == INSTALLER_CONTRACT.install_directory_name
    assert path.parent.name == "installer_staging"


def test_staging_uses_canonical_executable_name():
    result = stage_installation_package()

    assert result.success is True
    assert result.executable is not None
    assert result.executable.name == INSTALLER_CONTRACT.executable_name


def test_staged_executable_exists():
    result = stage_installation_package()

    assert result.success is True
    assert result.executable is not None
    assert result.executable.is_file()


def test_staged_package_contains_files():
    result = stage_installation_package()

    assert result.success is True
    assert result.files_copied > 1


def test_staged_package_contains_internal_runtime():
    result = stage_installation_package()

    assert result.success is True
    assert result.staging_root.joinpath("_internal").is_dir()
