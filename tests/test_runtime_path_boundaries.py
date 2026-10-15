from dataclasses import FrozenInstanceError

import pytest

from packaging.runtime_path_boundaries import (
    ApplicationPaths,
    resolve_application_paths,
)


def test_source_mode_uses_source_directory(tmp_path):
    module = tmp_path / "main.py"
    module.touch()

    paths = resolve_application_paths(
        "WindowsTechnician",
        module,
        is_frozen=False,
        environ={"LOCALAPPDATA": str(tmp_path / "Local")},
    )

    assert paths.application_root == tmp_path.resolve()
    assert paths.resource_root == tmp_path.resolve()
    assert paths.user_data_root == (
        tmp_path / "Local" / "WindowsTechnician"
    ).resolve()


def test_frozen_mode_separates_installation_and_bundle(tmp_path):
    install = tmp_path / "ProgramFiles" / "WindowsTechnician"
    bundle = tmp_path / "Temporary" / "_MEI12345"
    install.mkdir(parents=True)
    bundle.mkdir(parents=True)

    executable = install / "WindowsTechnician.exe"
    executable.touch()

    paths = resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=True,
        executable=executable,
        bundle_dir=bundle,
        environ={"LOCALAPPDATA": str(tmp_path / "Local")},
    )

    assert paths.application_root == install.resolve()
    assert paths.resource_root == bundle.resolve()
    assert paths.application_root != paths.resource_root


def test_local_app_data_takes_precedence(tmp_path):
    paths = resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=False,
        environ={
            "LOCALAPPDATA": str(tmp_path / "Local"),
            "APPDATA": str(tmp_path / "Roaming"),
        },
    )

    assert paths.user_data_root == (
        tmp_path / "Local" / "WindowsTechnician"
    ).resolve()


def test_roaming_app_data_is_fallback(tmp_path):
    paths = resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=False,
        environ={"APPDATA": str(tmp_path / "Roaming")},
    )

    assert paths.user_data_root == (
        tmp_path / "Roaming" / "WindowsTechnician"
    ).resolve()


def test_home_fallback_when_app_data_is_unavailable(tmp_path):
    paths = resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=False,
        environ={},
        home=tmp_path / "User",
    )

    assert paths.user_data_root == (
        tmp_path / "User" / ".local" / "share" / "WindowsTechnician"
    ).resolve()


@pytest.mark.parametrize("app_name", ["", " ", None])
def test_invalid_application_name_is_rejected(tmp_path, app_name):
    with pytest.raises(ValueError, match="app_name"):
        resolve_application_paths(
            app_name,
            tmp_path / "main.py",
            is_frozen=False,
            environ={},
        )


def test_path_resolution_does_not_create_user_data_directory(tmp_path):
    data_base = tmp_path / "Local"
    expected = data_base / "WindowsTechnician"

    resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=False,
        environ={"LOCALAPPDATA": str(data_base)},
    )

    assert not expected.exists()


def test_path_result_is_immutable(tmp_path):
    paths = resolve_application_paths(
        "WindowsTechnician",
        tmp_path / "main.py",
        is_frozen=False,
        environ={},
        home=tmp_path,
    )

    assert isinstance(paths, ApplicationPaths)

    with pytest.raises(FrozenInstanceError):
        paths.application_root = tmp_path / "other"
