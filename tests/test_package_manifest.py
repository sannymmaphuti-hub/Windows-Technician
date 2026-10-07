"""Tests for the production package manifest."""

from pathlib import Path

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.package_manifest import (
    PRODUCTION_PACKAGE_MANIFEST,
    manifest_path,
    required_files_exist,
)


def test_manifest_matches_application_metadata():
    assert (
        PRODUCTION_PACKAGE_MANIFEST.application_name
        == APPLICATION_METADATA.display_name
    )
    assert (
        PRODUCTION_PACKAGE_MANIFEST.version
        == APPLICATION_METADATA.version
    )


def test_manifest_defines_main_entry_point():
    assert PRODUCTION_PACKAGE_MANIFEST.entry_point == "main.py"


def test_manifest_contains_core_package_directories():
    expected = {
        "application",
        "diagnostics",
        "engine",
        "gui",
        "packaging",
    }

    assert expected.issubset(
        set(PRODUCTION_PACKAGE_MANIFEST.package_directories)
    )


def test_manifest_contains_resource_directory():
    assert "resources" in PRODUCTION_PACKAGE_MANIFEST.resource_directories


def test_manifest_contains_required_files():
    required = set(PRODUCTION_PACKAGE_MANIFEST.required_files)

    assert "main.py" in required
    assert "packaging/application_metadata.py" in required
    assert "packaging/resources.py" in required
    assert "packaging/runtime_configuration.py" in required


def test_manifest_paths_stay_inside_project():
    path = manifest_path("main.py")

    assert isinstance(path, Path)
    assert path.is_absolute()
    assert path == (Path.cwd() / "main.py").resolve()


def test_manifest_rejects_empty_path():
    with pytest.raises(ValueError):
        manifest_path("")


def test_manifest_rejects_project_escape():
    with pytest.raises(ValueError):
        manifest_path("..")


def test_required_files_exist():
    assert required_files_exist()
