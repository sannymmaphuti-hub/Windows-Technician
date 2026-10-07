"""Tests for configuration preservation during installation lifecycle."""

from pathlib import Path

import pytest

from packaging.configuration_preservation import (
    CONFIGURATION_PRESERVATION_CONTRACT,
    configuration_is_outside_installation,
    configuration_path,
)


def test_upgrade_preserves_configuration():
    assert (
        CONFIGURATION_PRESERVATION_CONTRACT.preserve_on_upgrade
        is True
    )


def test_uninstall_preserves_configuration():
    assert (
        CONFIGURATION_PRESERVATION_CONTRACT.preserve_on_uninstall
        is True
    )


def test_configuration_identity():
    assert (
        CONFIGURATION_PRESERVATION_CONTRACT.configuration_directory_name
        == "config"
    )
    assert (
        CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename
        == "settings.json"
    )


def test_configuration_path_is_user_scoped():
    root = Path(
        "C:/Users/Test/AppData/Local/WindowsTechnician"
    )

    assert configuration_path(root) == (
        root / "config" / "settings.json"
    )


def test_configuration_is_outside_installation():
    configuration = Path(
        "C:/Users/Test/AppData/Local/WindowsTechnician"
        "/config/settings.json"
    )

    install_root = Path(
        "C:/Program Files/Windows Technician"
    )

    assert configuration_is_outside_installation(
        configuration,
        install_root,
    )


def test_configuration_inside_installation_is_rejected():
    install_root = Path(
        "C:/Program Files/Windows Technician"
    )

    configuration = (
        install_root / "config" / "settings.json"
    )

    assert not configuration_is_outside_installation(
        configuration,
        install_root,
    )


def test_configuration_helpers_require_paths():
    with pytest.raises(TypeError):
        configuration_path("C:/Users/Test")

    with pytest.raises(TypeError):
        configuration_is_outside_installation(
            "C:/Users/Test/config/settings.json",
            Path("C:/Program Files/Windows Technician"),
        )

    with pytest.raises(TypeError):
        configuration_is_outside_installation(
            Path("C:/Users/Test/config/settings.json"),
            "C:/Program Files/Windows Technician",
        )


def test_configuration_contract_is_immutable():
    with pytest.raises(AttributeError):
        CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename = (
            "other.json"
        )
