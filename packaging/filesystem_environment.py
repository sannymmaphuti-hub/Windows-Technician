"""Production filesystem and path environment boundary."""

from dataclasses import dataclass
from pathlib import Path

from packaging.runtime_configuration import (
    RuntimePaths,
    default_runtime_paths,
)


@dataclass(frozen=True)
class FilesystemEnvironment:
    project_root: Path
    application_data: Path
    configuration: Path
    logs: Path
    reports: Path

    def __post_init__(self):
        for field_name in (
            "project_root",
            "application_data",
            "configuration",
            "logs",
            "reports",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, Path):
                raise TypeError(
                    f"{field_name} must be a Path."
                )


def build_filesystem_environment(
    *,
    project_root: Path,
    runtime_paths: RuntimePaths | None = None,
) -> FilesystemEnvironment:
    if not isinstance(project_root, Path):
        raise TypeError(
            "project_root must be a Path."
        )

    paths = runtime_paths or default_runtime_paths()

    if not isinstance(paths, RuntimePaths):
        raise TypeError(
            "runtime_paths must be RuntimePaths."
        )

    return FilesystemEnvironment(
        project_root=project_root.resolve(),
        application_data=paths.application_data.resolve(),
        configuration=paths.configuration.resolve(),
        logs=paths.logs.resolve(),
        reports=paths.reports.resolve(),
    )


def path_is_within(
    path: Path,
    boundary: Path,
) -> bool:
    if not isinstance(path, Path):
        raise TypeError(
            "path must be a Path."
        )

    if not isinstance(boundary, Path):
        raise TypeError(
            "boundary must be a Path."
        )

    try:
        path.resolve().relative_to(
            boundary.resolve()
        )
        return True
    except ValueError:
        return False


def filesystem_environment_is_valid(
    environment: FilesystemEnvironment,
) -> bool:
    if not isinstance(
        environment,
        FilesystemEnvironment,
    ):
        raise TypeError(
            "environment must be a FilesystemEnvironment."
        )

    return all(
        (
            path_is_within(
                environment.configuration,
                environment.application_data,
            ),
            path_is_within(
                environment.logs,
                environment.application_data,
            ),
            path_is_within(
                environment.reports,
                environment.application_data,
            ),
        )
    )
