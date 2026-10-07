"""Tests for safe production configuration defaults."""

import pytest

from packaging.safe_defaults import (
    SAFE_DEFAULTS,
    SafeDefaults,
    apply_safe_defaults,
    remediation_is_safe_by_default,
    remote_operations_are_disabled_by_default,
    safe_default_configuration,
    telemetry_is_disabled_by_default,
)


def test_safe_defaults_have_positive_configuration_version():
    assert SAFE_DEFAULTS.configuration_version > 0


def test_automatic_diagnostics_are_enabled_by_default():
    assert SAFE_DEFAULTS.automatic_diagnostics


def test_remediation_is_not_authorized_by_default():
    assert not SAFE_DEFAULTS.remediation_authorized_by_default


def test_remote_operations_are_disabled_by_default():
    assert not SAFE_DEFAULTS.remote_operations_enabled


def test_telemetry_is_disabled_by_default():
    assert not SAFE_DEFAULTS.telemetry_enabled


def test_logging_is_enabled_by_default():
    assert SAFE_DEFAULTS.logging_enabled


def test_default_theme_is_system():
    assert SAFE_DEFAULTS.ui_theme == "system"


def test_safe_defaults_are_immutable():
    with pytest.raises(AttributeError):
        SAFE_DEFAULTS.ui_theme = "dark"


def test_safe_defaults_require_positive_version():
    with pytest.raises(ValueError):
        SafeDefaults(
            configuration_version=0,
            automatic_diagnostics=True,
            remediation_authorized_by_default=False,
            remote_operations_enabled=False,
            telemetry_enabled=False,
            logging_enabled=True,
            ui_theme="system",
        )


def test_safe_defaults_require_boolean_values():
    with pytest.raises(TypeError):
        SafeDefaults(
            configuration_version=1,
            automatic_diagnostics="yes",
            remediation_authorized_by_default=False,
            remote_operations_enabled=False,
            telemetry_enabled=False,
            logging_enabled=True,
            ui_theme="system",
        )


def test_safe_defaults_require_theme():
    with pytest.raises(ValueError):
        SafeDefaults(
            configuration_version=1,
            automatic_diagnostics=True,
            remediation_authorized_by_default=False,
            remote_operations_enabled=False,
            telemetry_enabled=False,
            logging_enabled=True,
            ui_theme="",
        )


def test_default_configuration_contains_all_sections():
    configuration = safe_default_configuration()

    assert "version" in configuration
    assert "diagnostics" in configuration
    assert "remediation" in configuration
    assert "remote" in configuration
    assert "telemetry" in configuration
    assert "logging" in configuration
    assert "interface" in configuration


def test_default_configuration_disables_remediation_authorization():
    configuration = safe_default_configuration()

    assert (
        configuration["remediation"]["authorized_by_default"]
        is False
    )


def test_default_configuration_disables_remote_operations():
    configuration = safe_default_configuration()

    assert configuration["remote"]["enabled"] is False


def test_default_configuration_disables_telemetry():
    configuration = safe_default_configuration()

    assert configuration["telemetry"]["enabled"] is False


def test_apply_defaults_to_missing_configuration():
    configuration = apply_safe_defaults(None)

    assert configuration == safe_default_configuration()


def test_apply_defaults_to_empty_configuration():
    configuration = apply_safe_defaults({})

    assert configuration == safe_default_configuration()


def test_user_configuration_overrides_default():
    configuration = apply_safe_defaults(
        {
            "interface": {
                "theme": "dark",
            },
        }
    )

    assert configuration["interface"]["theme"] == "dark"


def test_user_configuration_does_not_remove_other_defaults():
    configuration = apply_safe_defaults(
        {
            "interface": {
                "theme": "dark",
            },
        }
    )

    assert configuration["remote"]["enabled"] is False
    assert configuration["telemetry"]["enabled"] is False
    assert (
        configuration["remediation"]["authorized_by_default"]
        is False
    )


def test_nested_configuration_is_merged():
    configuration = apply_safe_defaults(
        {
            "diagnostics": {
                "automatic_collection": False,
            },
        }
    )

    assert (
        configuration["diagnostics"]["automatic_collection"]
        is False
    )


def test_unknown_configuration_values_are_preserved():
    configuration = apply_safe_defaults(
        {
            "future_feature": {
                "enabled": True,
            },
        }
    )

    assert configuration["future_feature"]["enabled"] is True


def test_apply_defaults_requires_dictionary():
    with pytest.raises(TypeError):
        apply_safe_defaults("invalid")


def test_remediation_safety_contract():
    assert remediation_is_safe_by_default()


def test_remote_safety_contract():
    assert remote_operations_are_disabled_by_default()


def test_telemetry_safety_contract():
    assert telemetry_is_disabled_by_default()


def test_logging_remains_enabled_for_diagnostics():
    configuration = safe_default_configuration()

    assert configuration["logging"]["enabled"] is True
