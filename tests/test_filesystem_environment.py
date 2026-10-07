"""Tests for the filesystem and path environment boundary."""

from pathlib import Path

import pytest

from packaging.filesystem_environment import (
    FilesystemEnvironment,
    build_filesystem_environment,
    filesystem_environment_is_valid,
    path_is_within,
)
from packaging.runtime_configuration import (
    RuntimePaths,
)


def _runtime_paths(tmp_path):
    root = tmp_path / "WindowsTechnician"

    return RuntimePaths(
        application_data=root,
        configuration=root / "config",
        logs=root / "logs",
        reports=root / "reports",
    )


def test_filesystem_environment_contains_project_root(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    assert environment.project_root == tmp_path.resolve()


def test_filesystem_environment_contains_application_data(
    tmp_path,
):
    paths = _runtime_paths(tmp_path)

    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=paths,
    )

    assert environment.application_data == (
        paths.application_data.resolve()
    )


def test_filesystem_environment_contains_configuration(
    tmp_path,
):
    paths = _runtime_paths(tmp_path)

    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=paths,
    )

    assert environment.configuration == (
        paths.configuration.resolve()
    )


def test_filesystem_environment_contains_logs(
    tmp_path,
):
    paths = _runtime_paths(tmp_path)

    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=paths,
    )

    assert environment.logs == (
        paths.logs.resolve()
    )


def test_filesystem_environment_contains_reports(
    tmp_path,
):
    paths = _runtime_paths(tmp_path)

    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=paths,
    )

    assert environment.reports == (
        paths.reports.resolve()
    )


def test_filesystem_environment_requires_path_objects():
    with pytest.raises(TypeError):
        FilesystemEnvironment(
            project_root="invalid",
            application_data=Path("data"),
            configuration=Path("config"),
            logs=Path("logs"),
            reports=Path("reports"),
        )


def test_path_is_within_accepts_contained_path(
    tmp_path,
):
    boundary = tmp_path / "root"
    path = boundary / "logs" / "app.log"

    assert path_is_within(
        path,
        boundary,
    )


def test_path_is_within_rejects_outside_path(
    tmp_path,
):
    boundary = tmp_path / "root"
    path = tmp_path / "outside" / "app.log"

    assert not path_is_within(
        path,
        boundary,
    )


def test_path_is_within_rejects_path_traversal(
    tmp_path,
):
    boundary = tmp_path / "root"
    path = boundary / ".." / "outside"

    assert not path_is_within(
        path,
        boundary,
    )


def test_path_is_within_requires_path():
    with pytest.raises(TypeError):
        path_is_within(
            "invalid",
            Path("root"),
        )


def test_path_is_within_requires_boundary():
    with pytest.raises(TypeError):
        path_is_within(
            Path("file"),
            "invalid",
        )


def test_filesystem_environment_is_valid(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    assert filesystem_environment_is_valid(
        environment
    )


def test_filesystem_environment_validation_requires_environment():
    with pytest.raises(TypeError):
        filesystem_environment_is_valid(
            "invalid"
        )


def test_filesystem_environment_is_immutable(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    with pytest.raises(AttributeError):
        environment.logs = tmp_path / "changed"


def test_runtime_paths_are_preserved(
    tmp_path,
):
    paths = _runtime_paths(tmp_path)

    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=paths,
    )

    assert environment.application_data == (
        paths.application_data.resolve()
    )
    assert environment.configuration == (
        paths.configuration.resolve()
    )
    assert environment.logs == (
        paths.logs.resolve()
    )
    assert environment.reports == (
        paths.reports.resolve()
    )


def test_configuration_is_inside_application_data(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    assert path_is_within(
        environment.configuration,
        environment.application_data,
    )


def test_logs_are_inside_application_data(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    assert path_is_within(
        environment.logs,
        environment.application_data,
    )


def test_reports_are_inside_application_data(
    tmp_path,
):
    environment = build_filesystem_environment(
        project_root=tmp_path,
        runtime_paths=_runtime_paths(tmp_path),
    )

    assert path_is_within(
        environment.reports,
        environment.application_data,
    )
