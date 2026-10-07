"""Production packaging architecture contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA
from packaging.package_manifest import PRODUCTION_PACKAGE_MANIFEST
from packaging.runtime_configuration import default_runtime_paths
from packaging.resources import RESOURCE_ROOT


@dataclass(frozen=True)
class PackagingArchitecture:
    application_name: str
    version: str
    entry_point: str
    package_root: Path
    resource_root: Path
    runtime_data_root_name: str


PACKAGING_ARCHITECTURE = PackagingArchitecture(
    application_name=APPLICATION_METADATA.display_name,
    version=APPLICATION_METADATA.version,
    entry_point=PRODUCTION_PACKAGE_MANIFEST.entry_point,
    package_root=Path(__file__).resolve().parent,
    resource_root=RESOURCE_ROOT,
    runtime_data_root_name=default_runtime_paths().application_data.name,
)


def packaging_architecture_is_consistent() -> bool:
    return (
        PACKAGING_ARCHITECTURE.application_name
        == APPLICATION_METADATA.display_name
        and PACKAGING_ARCHITECTURE.version
        == APPLICATION_METADATA.version
        and PACKAGING_ARCHITECTURE.entry_point
        == PRODUCTION_PACKAGE_MANIFEST.entry_point
        and PACKAGING_ARCHITECTURE.resource_root
        == RESOURCE_ROOT
    )
