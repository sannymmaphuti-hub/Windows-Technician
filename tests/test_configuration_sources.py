"""Tests for user and system configuration."""

from pathlib import Path
import json

import pytest

from packaging.configuration_sources import (
    ConfigurationLocations,
    ConfigurationSources,
    build_configuration_locations,
    load_configuration_file,
    load_configuration_sources,
    merge_configuration,
    user_configuration_overrides_system,
)


def test_configuration_locations_are_paths(tmp_path):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    assert isinstance(
        locations.user_configuration,
        Path,
    )

    assert isinstance(
        locations.system_configuration,
        Path,
    )


def test_user_configuration_has_expected_location(tmp_path):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    assert locations.user_configuration == (
        tmp_path
        / "user"
        / "config"
        / "settings.json"
    )


def test_system_configuration_has_expected_location(tmp_path):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    assert locations.system_configuration == (
        tmp_path
        / "system"
        / "config"
        / "system.json"
    )


def test_locations_require_paths():
    with pytest.raises(TypeError):
        ConfigurationLocations(
            user_configuration="invalid",
            system_configuration=Path("system"),
        )


def test_configuration_sources_require_dictionaries():
    with pytest.raises(TypeError):
        ConfigurationSources(
            user="invalid",
            system={},
        )


def test_missing_configuration_file_returns_empty_dict(
    tmp_path,
):
    result = load_configuration_file(
        tmp_path / "missing.json"
    )

    assert result == {}


def test_configuration_file_is_loaded(tmp_path):
    path = tmp_path / "settings.json"

    path.write_text(
        json.dumps(
            {
                "theme": "dark",
                "diagnostics": True,
            }
        ),
        encoding="utf-8",
    )

    result = load_configuration_file(path)

    assert result["theme"] == "dark"
    assert result["diagnostics"] is True


def test_configuration_file_must_be_file(tmp_path):
    path = tmp_path / "settings"

    path.mkdir()

    with pytest.raises(ValueError):
        load_configuration_file(path)


def test_configuration_file_requires_json_object(
    tmp_path,
):
    path = tmp_path / "settings.json"

    path.write_text(
        json.dumps(["invalid"]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_configuration_file(path)


def test_configuration_file_requires_path():
    with pytest.raises(TypeError):
        load_configuration_file("invalid")


def test_configuration_sources_load_user_and_system(
    tmp_path,
):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    locations.user_configuration.parent.mkdir(
        parents=True,
    )

    locations.system_configuration.parent.mkdir(
        parents=True,
    )

    locations.user_configuration.write_text(
        json.dumps(
            {
                "theme": "dark",
                "user_setting": True,
            }
        ),
        encoding="utf-8",
    )

    locations.system_configuration.write_text(
        json.dumps(
            {
                "theme": "light",
                "system_setting": True,
            }
        ),
        encoding="utf-8",
    )

    sources = load_configuration_sources(
        locations
    )

    assert sources.user["theme"] == "dark"
    assert sources.system["theme"] == "light"
    assert sources.user["user_setting"] is True
    assert sources.system["system_setting"] is True


def test_missing_sources_are_empty(
    tmp_path,
):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    sources = load_configuration_sources(
        locations
    )

    assert sources.user == {}
    assert sources.system == {}


def test_merge_uses_system_as_base():
    sources = ConfigurationSources(
        user={
            "theme": "dark",
            "user_setting": True,
        },
        system={
            "theme": "light",
            "system_setting": True,
        },
    )

    merged = merge_configuration(sources)

    assert merged["theme"] == "dark"
    assert merged["system_setting"] is True
    assert merged["user_setting"] is True


def test_user_configuration_overrides_system():
    sources = ConfigurationSources(
        user={
            "theme": "dark",
        },
        system={
            "theme": "light",
        },
    )

    assert user_configuration_overrides_system(
        sources,
        "theme",
    )


def test_same_value_is_not_an_override():
    sources = ConfigurationSources(
        user={
            "theme": "dark",
        },
        system={
            "theme": "dark",
        },
    )

    assert not user_configuration_overrides_system(
        sources,
        "theme",
    )


def test_missing_key_is_not_an_override():
    sources = ConfigurationSources(
        user={},
        system={
            "theme": "light",
        },
    )

    assert not user_configuration_overrides_system(
        sources,
        "theme",
    )


def test_override_requires_valid_key():
    sources = ConfigurationSources(
        user={},
        system={},
    )

    with pytest.raises(ValueError):
        user_configuration_overrides_system(
            sources,
            "",
        )


def test_merge_requires_sources():
    with pytest.raises(TypeError):
        merge_configuration("invalid")


def test_load_sources_requires_locations():
    with pytest.raises(TypeError):
        load_configuration_sources("invalid")


def test_configuration_locations_are_immutable(tmp_path):
    locations = build_configuration_locations(
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    with pytest.raises(AttributeError):
        locations.user_configuration = Path("changed")


def test_configuration_sources_are_immutable():
    sources = ConfigurationSources(
        user={},
        system={},
    )

    with pytest.raises(AttributeError):
        sources.user = {}
