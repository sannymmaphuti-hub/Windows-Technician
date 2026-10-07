"""Tests for the Windows Technician shortcut contract."""

from pathlib import Path

import pytest

from packaging.shortcut_contract import (
    SHORTCUT_CONTRACT,
    shortcut_is_installation_bound,
    shortcut_target,
    shortcut_working_directory,
)


def test_shortcut_matches_installer_identity():
    assert SHORTCUT_CONTRACT.name == "Windows Technician"
    assert SHORTCUT_CONTRACT.target_name == "WindowsTechnician.exe"


def test_shortcut_start_menu_identity():
    assert SHORTCUT_CONTRACT.start_menu_name == "Windows Technician"


def test_shortcut_desktop_identity():
    assert SHORTCUT_CONTRACT.desktop_name == "Windows Technician"


def test_shortcut_working_directory_identity():
    assert SHORTCUT_CONTRACT.working_directory_name == "Windows Technician"


def test_shortcut_target_is_inside_installation():
    install_root = Path("C:/Program Files/Windows Technician")

    target = shortcut_target(install_root)

    assert target == (
        install_root / "WindowsTechnician.exe"
    )


def test_shortcut_working_directory_is_installation_root():
    install_root = Path("C:/Program Files/Windows Technician")

    assert shortcut_working_directory(install_root) == install_root


def test_shortcut_target_is_installation_bound():
    install_root = Path("C:/Program Files/Windows Technician")
    target = shortcut_target(install_root)

    assert shortcut_is_installation_bound(
        install_root,
        target,
    )


def test_development_repository_cannot_be_shortcut_target():
    install_root = Path("C:/Program Files/Windows Technician")
    development_target = Path(
        "C:/Users/Acer/Desktop/Windows Technician V0.5 Project/main.py"
    )

    assert not shortcut_is_installation_bound(
        install_root,
        development_target,
    )


def test_shortcut_contract_is_immutable():
    with pytest.raises(AttributeError):
        SHORTCUT_CONTRACT.name = "Something Else"


def test_shortcut_helpers_require_paths():
    with pytest.raises(TypeError):
        shortcut_target("C:/Program Files/Windows Technician")

    with pytest.raises(TypeError):
        shortcut_working_directory(
            "C:/Program Files/Windows Technician"
        )

    with pytest.raises(TypeError):
        shortcut_is_installation_bound(
            "C:/Program Files/Windows Technician",
            Path("C:/Program Files/Windows Technician/WindowsTechnician.exe"),
        )
