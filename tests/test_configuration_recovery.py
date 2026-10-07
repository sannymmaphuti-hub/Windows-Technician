"""Tests for configuration recovery."""

import json

import pytest

from packaging.configuration_recovery import (
    ConfigurationRecovery,
    default_configuration,
    load_configuration,
    save_configuration,
)


def test_missing_configuration_uses_defaults(tmp_path):
    path = tmp_path / "settings.json"

    result = load_configuration(path)

    assert result.recovered is True
    assert result.source == "defaults"
    assert result.configuration == default_configuration()
    assert result.quarantined_path is None


def test_valid_configuration_loads_normally(tmp_path):
    path = tmp_path / "settings.json"

    configuration = {
        "version": 1,
        "interface": {
            "theme": "dark",
        },
    }

    save_configuration(path, configuration)

    result = load_configuration(path)

    assert result.recovered is False
    assert result.source == "file"
    assert result.configuration == configuration
    assert result.quarantined_path is None


def test_corrupt_json_is_quarantined(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        '{"broken": ',
        encoding="utf-8",
    )

    result = load_configuration(path)

    assert result.recovered is True
    assert result.source == "recovered"
    assert result.configuration == default_configuration()
    assert result.quarantined_path is not None
    assert result.quarantined_path.exists()
    assert not path.exists()


def test_quarantined_file_preserves_original_content(tmp_path):
    path = tmp_path / "settings.json"
    original = '{"broken": '

    path.write_text(
        original,
        encoding="utf-8",
    )

    result = load_configuration(path)

    assert result.quarantined_path is not None
    assert result.quarantined_path.read_text(
        encoding="utf-8"
    ) == original


def test_non_dictionary_configuration_is_recovered(tmp_path):
    path = tmp_path / "settings.json"

    path.write_text(
        json.dumps(["not", "a", "configuration"]),
        encoding="utf-8",
    )

    result = load_configuration(path)

    assert result.recovered is True
    assert result.source == "recovered"
    assert result.configuration == default_configuration()
    assert result.quarantined_path is not None
    assert result.quarantined_path.exists()


def test_quarantine_uses_unique_name(tmp_path):
    path = tmp_path / "settings.json"

    path.write_text(
        '{"broken": ',
        encoding="utf-8",
    )

    first = load_configuration(path)

    assert first.quarantined_path is not None

    path.write_text(
        '{"broken again": ',
        encoding="utf-8",
    )

    second = load_configuration(path)

    assert second.quarantined_path is not None
    assert second.quarantined_path != first.quarantined_path
    assert second.quarantined_path.exists()
    assert first.quarantined_path.exists()


def test_configuration_path_must_be_path(tmp_path):
    with pytest.raises(TypeError):
        load_configuration(
            str(tmp_path / "settings.json")
        )


def test_save_requires_dictionary(tmp_path):
    with pytest.raises(TypeError):
        save_configuration(
            tmp_path / "settings.json",
            [],
        )


def test_save_and_reload_round_trip(tmp_path):
    path = tmp_path / "settings.json"

    configuration = {
        "version": 1,
        "diagnostics": {
            "automatic_collection": False,
        },
    }

    save_configuration(path, configuration)

    result = load_configuration(path)

    assert result.recovered is False
    assert result.configuration == configuration


def test_recovery_result_is_immutable(tmp_path):
    result = load_configuration(
        tmp_path / "settings.json"
    )

    with pytest.raises(AttributeError):
        result.recovered = False


def test_recovery_object_has_expected_shape(tmp_path):
    result = load_configuration(
        tmp_path / "settings.json"
    )

    assert isinstance(result, ConfigurationRecovery)
    assert isinstance(result.configuration, dict)
    assert isinstance(result.source, str)
