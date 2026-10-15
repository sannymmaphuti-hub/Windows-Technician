"""Tests for the Windows Technician upgrade contract."""

import pytest

from packaging.upgrade_contract import (
    UPGRADE_CONTRACT,
    is_downgrade,
    is_newer_version,
    is_same_version,
    upgrade_preserves_user_data,
)


def test_upgrade_matches_application_identity():
    assert UPGRADE_CONTRACT.application_name == "Windows Technician"
    assert UPGRADE_CONTRACT.current_version.startswith("1.0.")


def test_upgrade_replaces_application_files():
    assert UPGRADE_CONTRACT.replace_application_files is True


def test_upgrade_replaces_resources():
    assert UPGRADE_CONTRACT.replace_resources is True


def test_upgrade_preserves_configuration():
    assert UPGRADE_CONTRACT.preserve_configuration is True


def test_upgrade_preserves_logs():
    assert UPGRADE_CONTRACT.preserve_logs is True


def test_upgrade_preserves_reports():
    assert UPGRADE_CONTRACT.preserve_reports is True


def test_upgrade_preserves_shortcuts():
    assert UPGRADE_CONTRACT.preserve_shortcuts is True


def test_downgrade_is_not_allowed():
    assert UPGRADE_CONTRACT.allow_downgrade is False


def test_newer_version_is_detected():
    assert is_newer_version(
        (0, 9, 0),
        (0, 9, 1),
    )


def test_same_version_is_detected():
    assert is_same_version(
        (0, 9, 0),
        (0, 9, 0),
    )


def test_downgrade_is_detected():
    assert is_downgrade(
        (0, 9, 1),
        (0, 9, 0),
    )


def test_version_comparison_handles_multiple_components():
    assert is_newer_version(
        (0, 9, 9),
        (0, 10, 0),
    )


def test_upgrade_preserves_user_data():
    assert upgrade_preserves_user_data() is True


def test_upgrade_contract_is_immutable():
    with pytest.raises(AttributeError):
        UPGRADE_CONTRACT.allow_downgrade = True
