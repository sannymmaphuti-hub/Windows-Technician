"""Tests for the Windows Technician uninstall contract."""

import pytest

from packaging.uninstall_contract import (
    UNINSTALL_CONTRACT,
    uninstall_is_application_only_by_default,
    uninstall_preserves_user_data_by_default,
    user_data_may_be_removed,
)


def test_uninstall_removes_application_files():
    assert UNINSTALL_CONTRACT.remove_application_files is True


def test_uninstall_removes_resources():
    assert UNINSTALL_CONTRACT.remove_resources is True


def test_uninstall_removes_start_menu_shortcut():
    assert UNINSTALL_CONTRACT.remove_start_menu_shortcut is True


def test_uninstall_removes_desktop_shortcut():
    assert UNINSTALL_CONTRACT.remove_desktop_shortcut is True


def test_uninstall_preserves_configuration():
    assert UNINSTALL_CONTRACT.preserve_configuration is True


def test_uninstall_preserves_logs():
    assert UNINSTALL_CONTRACT.preserve_logs is True


def test_uninstall_preserves_reports():
    assert UNINSTALL_CONTRACT.preserve_reports is True


def test_user_data_requires_explicit_confirmation():
    assert (
        UNINSTALL_CONTRACT.require_explicit_user_data_confirmation
        is True
    )


def test_user_data_is_preserved_without_confirmation():
    assert user_data_may_be_removed(False) is False


def test_user_data_can_be_removed_with_confirmation():
    assert user_data_may_be_removed(True) is True


def test_uninstall_preserves_user_data_by_default():
    assert uninstall_preserves_user_data_by_default() is True


def test_uninstall_is_application_only_by_default():
    assert uninstall_is_application_only_by_default() is True


def test_uninstall_contract_is_immutable():
    with pytest.raises(AttributeError):
        UNINSTALL_CONTRACT.preserve_logs = False
