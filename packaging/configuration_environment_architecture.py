"""Integrated configuration and environment architecture."""

from dataclasses import dataclass
from pathlib import Path

from packaging.configuration_sources import (
    ConfigurationLocations,
    ConfigurationSources,
    build_configuration_locations,
    load_configuration_sources,
    merge_configuration,
)
from packaging.filesystem_environment import (
    FilesystemEnvironment,
    build_filesystem_environment,
)
from packaging.permission_context import (
    PermissionContext,
    detect_permission_context,
)
from packaging.safe_defaults import (
    SAFE_DEFAULTS,
    apply_safe_defaults,
)
from packaging.windows_environment import (
    WindowsEnvironment,
    detect_windows_environment,
)


@dataclass(frozen=True)
class ConfigurationEnvironmentArchitecture:
    windows: WindowsEnvironment
    permissions: PermissionContext
    filesystem: FilesystemEnvironment
    configuration_locations: ConfigurationLocations
    configuration_sources: ConfigurationSources
    effective_configuration: dict

    @property
    def application_version(self) -> str:
        return self.windows.application_version

    @property
    def remediation_authorized_by_default(self) -> bool:
        return bool(
            self.effective_configuration[
                "remediation"
            ][
                "authorized_by_default"
            ]
        )

    @property
    def remote_operations_enabled(self) -> bool:
        return bool(
            self.effective_configuration[
                "remote"
            ][
                "enabled"
            ]
        )

    @property
    def telemetry_enabled(self) -> bool:
        return bool(
            self.effective_configuration[
                "telemetry"
            ][
                "enabled"
            ]
        )


def build_configuration_environment_architecture(
    *,
    project_root: Path,
    user_data_root: Path,
    system_data_root: Path,
    windows_environment: WindowsEnvironment | None = None,
    permission_context: PermissionContext | None = None,
) -> ConfigurationEnvironmentArchitecture:
    windows = (
        windows_environment
        or detect_windows_environment()
    )

    permissions = (
        permission_context
        or detect_permission_context()
    )

    filesystem = build_filesystem_environment(
        project_root=project_root,
    )

    locations = build_configuration_locations(
        user_data_root=user_data_root,
        system_data_root=system_data_root,
    )

    sources = load_configuration_sources(
        locations
    )

    merged = merge_configuration(sources)
    effective = apply_safe_defaults(merged)

    return ConfigurationEnvironmentArchitecture(
        windows=windows,
        permissions=permissions,
        filesystem=filesystem,
        configuration_locations=locations,
        configuration_sources=sources,
        effective_configuration=effective,
    )


def configuration_environment_is_safe(
    architecture: ConfigurationEnvironmentArchitecture,
) -> bool:
    if not isinstance(
        architecture,
        ConfigurationEnvironmentArchitecture,
    ):
        raise TypeError(
            "architecture must be "
            "ConfigurationEnvironmentArchitecture."
        )

    configuration = architecture.effective_configuration

    remediation = configuration.get(
        "remediation",
        {},
    )

    remote = configuration.get(
        "remote",
        {},
    )

    telemetry = configuration.get(
        "telemetry",
        {},
    )

    return (
        architecture.windows.supports_application
        and isinstance(
            architecture.permissions,
            PermissionContext,
        )
        and isinstance(
            architecture.filesystem,
            FilesystemEnvironment,
        )
        and remediation.get(
            "authorized_by_default",
            True,
        )
        is False
        and remote.get(
            "enabled",
            True,
        )
        is False
        and telemetry.get(
            "enabled",
            True,
        )
        is False
    )


def configuration_environment_is_consistent(
    architecture: ConfigurationEnvironmentArchitecture,
) -> bool:
    if not isinstance(
        architecture,
        ConfigurationEnvironmentArchitecture,
    ):
        raise TypeError(
            "architecture must be "
            "ConfigurationEnvironmentArchitecture."
        )

    return (
        architecture.windows.application_version
        == architecture.effective_configuration.get(
            "application_version",
            architecture.windows.application_version,
        )
    )


def default_configuration_environment_architecture(
    *,
    project_root: Path,
    user_data_root: Path,
    system_data_root: Path,
) -> ConfigurationEnvironmentArchitecture:
    return build_configuration_environment_architecture(
        project_root=project_root,
        user_data_root=user_data_root,
        system_data_root=system_data_root,
    )
