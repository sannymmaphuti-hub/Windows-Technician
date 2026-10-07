from pathlib import Path

import pytest

from packaging.resources import (
    RESOURCE_ROOT,
    resource_exists,
    resource_path,
    resource_root,
)


def test_resource_root_is_canonical_directory():
    assert resource_root() == RESOURCE_ROOT
    assert resource_root().name == "resources"


def test_resource_root_exists():
    assert resource_root().is_dir()


def test_resource_categories_exist():
    assert (RESOURCE_ROOT / "icons").is_dir()
    assert (RESOURCE_ROOT / "application").is_dir()


def test_resource_path_resolves_inside_boundary():
    path = resource_path("icons", "test.ico")

    assert path.parent == RESOURCE_ROOT / "icons"
    assert path.is_absolute()


def test_resource_path_rejects_empty_path():
    with pytest.raises(ValueError):
        resource_path()


def test_resource_path_rejects_boundary_escape():
    with pytest.raises(ValueError):
        resource_path("..", "outside.txt")


def test_resource_exists_reports_existing_resource():
    assert resource_exists("README.md")


def test_resource_exists_reports_missing_resource():
    assert not resource_exists("icons", "does-not-exist.ico")
