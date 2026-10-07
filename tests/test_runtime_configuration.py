import os
from pathlib import Path

import pytest

from packaging.runtime_configuration import (
    RuntimePaths,
    default_runtime_paths,
    initialize_runtime_paths,
)


def test_default_runtime_paths_are_user_scoped():
    paths = default_runtime_paths()

    assert paths.application_data.name == "WindowsTechnician"
    assert paths.configuration == paths.application_data / "config"
    assert paths.logs == paths.application_data / "logs"
    assert paths.reports == paths.application_data / "reports"


def test_default_runtime_paths_do_not_use_project_directory():
    paths = default_runtime_paths()

    project_root = Path.cwd().resolve()

    assert paths.application_data.resolve() != project_root
    assert project_root not in paths.application_data.resolve().parents


def test_runtime_paths_are_constructed_under_application_data():
    paths = default_runtime_paths()

    assert paths.configuration.parent == paths.application_data
    assert paths.logs.parent == paths.application_data
    assert paths.reports.parent == paths.application_data


def test_runtime_paths_can_be_initialized(tmp_path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "app" / "config",
        logs=tmp_path / "app" / "logs",
        reports=tmp_path / "app" / "reports",
    )

    result = initialize_runtime_paths(paths)

    assert result == paths
    assert paths.application_data.is_dir()
    assert paths.configuration.is_dir()
    assert paths.logs.is_dir()
    assert paths.reports.is_dir()


def test_runtime_initialization_is_idempotent(tmp_path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "app" / "config",
        logs=tmp_path / "app" / "logs",
        reports=tmp_path / "app" / "reports",
    )

    initialize_runtime_paths(paths)
    initialize_runtime_paths(paths)

    assert paths.application_data.is_dir()
    assert paths.configuration.is_dir()
    assert paths.logs.is_dir()
    assert paths.reports.is_dir()


def test_runtime_paths_remain_under_application_data(tmp_path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "app" / "config",
        logs=tmp_path / "app" / "logs",
        reports=tmp_path / "app" / "reports",
    )

    root = paths.application_data.resolve()

    for child in (
        paths.configuration,
        paths.logs,
        paths.reports,
    ):
        assert root in child.resolve().parents


def test_runtime_paths_require_directory_paths(tmp_path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "app" / "config",
        logs=tmp_path / "app" / "logs",
        reports=tmp_path / "app" / "reports",
    )

    assert all(
        isinstance(path, Path)
        for path in (
            paths.application_data,
            paths.configuration,
            paths.logs,
            paths.reports,
        )
    )
