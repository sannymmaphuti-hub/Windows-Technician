"""Production package manifest contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA


@dataclass(frozen=True)
class PackageManifest:
    application_name: str
    version: str
    entry_point: str
    package_directories: tuple[str, ...]
    resource_directories: tuple[str, ...]
    required_files: tuple[str, ...]

    def __post_init__(self):
        if self.application_name != APPLICATION_METADATA.display_name:
            raise ValueError(
                "Package manifest application name must match application metadata."
            )

        if self.version != APPLICATION_METADATA.version:
            raise ValueError(
                "Package manifest version must match application metadata."
            )

        if not self.entry_point.strip():
            raise ValueError("entry_point must be non-empty.")

        if not self.package_directories:
            raise ValueError("At least one package directory is required.")

        if not self.required_files:
            raise ValueError("At least one required file is required.")


PROJECT_ROOT = Path(__file__).resolve().parent.parent


PRODUCTION_PACKAGE_MANIFEST = PackageManifest(
    application_name=APPLICATION_METADATA.display_name,
    version=APPLICATION_METADATA.version,
    entry_point="main.py",
    package_directories=(
        "application",
        "diagnostics",
        "engine",
        "gui",
        "packaging",
    ),
    resource_directories=(
        "resources",
    ),
    required_files=(
        "main.py",
        "packaging/application_metadata.py",
        "packaging/resources.py",
        "packaging/runtime_configuration.py",
    ),
)


def manifest_path(relative_path: str) -> Path:
    """Resolve a manifest path without allowing it to escape the project."""
    if not relative_path or not relative_path.strip():
        raise ValueError("relative_path must be non-empty.")

    candidate = (PROJECT_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            "Manifest path escapes the project boundary."
        ) from exc

    return candidate


def required_files_exist() -> bool:
    """Return whether every manifest-required file currently exists."""
    return all(
        manifest_path(path).is_file()
        for path in PRODUCTION_PACKAGE_MANIFEST.required_files
    )
