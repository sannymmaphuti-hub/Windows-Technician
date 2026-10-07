"""Integration tests for the production packaging architecture."""

from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA
from packaging.package_manifest import PRODUCTION_PACKAGE_MANIFEST
from packaging.packaging_architecture import (
    PACKAGING_ARCHITECTURE,
    packaging_architecture_is_consistent,
)
from packaging.resources import RESOURCE_ROOT
from packaging.runtime_configuration import default_runtime_paths


def test_packaging_architecture_matches_metadata():
    assert (
        PACKAGING_ARCHITECTURE.application_name
        == APPLICATION_METADATA.display_name
    )
    assert PACKAGING_ARCHITECTURE.version == APPLICATION_METADATA.version


def test_packaging_architecture_matches_manifest():
    assert (
        PACKAGING_ARCHITECTURE.entry_point
        == PRODUCTION_PACKAGE_MANIFEST.entry_point
    )


def test_packaging_architecture_uses_resource_boundary():
    assert PACKAGING_ARCHITECTURE.resource_root == RESOURCE_ROOT


def test_packaging_architecture_has_runtime_data_identity():
    paths = default_runtime_paths()

    assert (
        PACKAGING_ARCHITECTURE.runtime_data_root_name
        == paths.application_data.name
    )


def test_packaging_architecture_package_root_exists():
    assert isinstance(PACKAGING_ARCHITECTURE.package_root, Path)
    assert PACKAGING_ARCHITECTURE.package_root.is_dir()


def test_packaging_architecture_is_consistent():
    assert packaging_architecture_is_consistent()


def test_production_packaging_identity_is_v09_beta():
    assert PACKAGING_ARCHITECTURE.application_name == "Windows Technician"
    assert PACKAGING_ARCHITECTURE.version.startswith("0.9.")
