"""Tests for the Windows permission and privilege boundary."""

from unittest.mock import patch

import pytest

from packaging.permission_context import (
    PermissionContext,
    detect_permission_context,
    permission_context_is_valid,
)


def test_permission_context_contains_user_name():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=True,
        is_elevated=True,
        can_write_program_files=True,
        can_write_system_directory=True,
    )

    assert context.user_name == "Sanny"


def test_privileged_access_requires_admin_and_elevation():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=True,
        is_elevated=True,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    assert context.has_privileged_access


def test_admin_without_elevation_is_not_privileged():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=True,
        is_elevated=False,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    assert not context.has_privileged_access


def test_elevation_without_admin_is_not_privileged():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=False,
        is_elevated=True,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    assert not context.has_privileged_access


def test_permission_context_is_immutable():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=False,
        is_elevated=False,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    with pytest.raises(AttributeError):
        context.is_admin = True


def test_permission_context_requires_user_name():
    context = PermissionContext(
        user_name="Sanny",
        is_admin=False,
        is_elevated=False,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    assert permission_context_is_valid(context)


def test_invalid_permission_context_type():
    with pytest.raises(TypeError):
        permission_context_is_valid("invalid")


def test_permission_detection_returns_context():
    context = detect_permission_context()

    assert isinstance(
        context,
        PermissionContext,
    )


def test_detected_user_name_is_non_empty():
    context = detect_permission_context()

    assert context.user_name


def test_detected_admin_state_is_boolean():
    context = detect_permission_context()

    assert isinstance(
        context.is_admin,
        bool,
    )


def test_detected_elevation_state_is_boolean():
    context = detect_permission_context()

    assert isinstance(
        context.is_elevated,
        bool,
    )


def test_detected_program_files_access_is_boolean():
    context = detect_permission_context()

    assert isinstance(
        context.can_write_program_files,
        bool,
    )


def test_detected_system_directory_access_is_boolean():
    context = detect_permission_context()

    assert isinstance(
        context.can_write_system_directory,
        bool,
    )


def test_non_windows_environment_is_not_admin():
    with patch(
        "packaging.permission_context.os.name",
        "posix",
    ):
        assert not __import__(
            "packaging.permission_context",
            fromlist=["_detect_admin"],
        )._detect_admin()


def test_admin_detection_handles_missing_windows_api():
    with patch(
        "packaging.permission_context.os.name",
        "nt",
    ), patch(
        "packaging.permission_context.ctypes.windll.shell32.IsUserAnAdmin",
        side_effect=AttributeError,
    ):
        from packaging.permission_context import _detect_admin

        assert not _detect_admin()


def test_permission_context_is_valid_requires_name():
    context = PermissionContext(
        user_name=" ",
        is_admin=False,
        is_elevated=False,
        can_write_program_files=False,
        can_write_system_directory=False,
    )

    assert not permission_context_is_valid(context)
