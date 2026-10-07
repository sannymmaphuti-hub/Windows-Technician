import pytest

from engine.application_configuration import (
    ApplicationConfiguration,
)


def test_default_configuration():
    configuration = ApplicationConfiguration()

    assert configuration.to_dict() == {
        "ui": {
            "theme": "system",
            "compact_mode": False,
        },
        "diagnostics": {
            "enabled": True,
            "collect_system_information": True,
        },
        "fleet": {
            "enabled": False,
            "max_machines": 1,
        },
        "safety": {
            "require_remediation_authorization": True,
            "allow_automatic_remediation": False,
        },
    }


def test_custom_values_override_defaults():
    configuration = ApplicationConfiguration(
        {
            "ui": {
                "theme": "dark",
            },
            "fleet": {
                "enabled": True,
                "max_machines": 25,
            },
        }
    )

    assert configuration.get(
        "ui",
        "theme",
    ) == "dark"

    assert configuration.get(
        "fleet",
        "enabled",
    ) is True

    assert configuration.get(
        "fleet",
        "max_machines",
    ) == 25

    assert configuration.get(
        "diagnostics",
        "enabled",
    ) is True


def test_nested_defaults_are_preserved():
    configuration = ApplicationConfiguration(
        {
            "ui": {
                "theme": "light",
            }
        }
    )

    assert configuration.section("ui") == {
        "theme": "light",
        "compact_mode": False,
    }


def test_invalid_configuration_type_is_rejected():
    with pytest.raises(ValueError):
        ApplicationConfiguration([])


def test_invalid_theme_is_rejected():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "ui": {
                    "theme": "blue",
                }
            }
        )


def test_compact_mode_requires_boolean():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "ui": {
                    "compact_mode": "yes",
                }
            }
        )


def test_diagnostics_enabled_requires_boolean():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "diagnostics": {
                    "enabled": "yes",
                }
            }
        )


def test_system_information_requires_boolean():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "diagnostics": {
                    "collect_system_information": 1,
                }
            }
        )


def test_fleet_enabled_requires_boolean():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "fleet": {
                    "enabled": "yes",
                }
            }
        )


def test_fleet_machine_limit_must_be_positive_integer():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "fleet": {
                    "max_machines": 0,
                }
            }
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        0,
        1.5,
        True,
        "10",
    ],
)
def test_invalid_machine_limits(value):
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "fleet": {
                    "max_machines": value,
                }
            }
        )


def test_remediation_authorization_defaults_safe():
    configuration = ApplicationConfiguration()

    assert configuration.get(
        "safety",
        "require_remediation_authorization",
    ) is True

    assert configuration.get(
        "safety",
        "allow_automatic_remediation",
    ) is False


def test_unsafe_automatic_remediation_configuration_is_rejected():
    with pytest.raises(ValueError):
        ApplicationConfiguration(
            {
                "safety": {
                    "require_remediation_authorization": False,
                    "allow_automatic_remediation": True,
                }
            }
        )


def test_get_returns_default_for_missing_key():
    configuration = ApplicationConfiguration()

    assert configuration.get(
        "ui",
        "missing",
        "fallback",
    ) == "fallback"


def test_unknown_section_is_rejected():
    configuration = ApplicationConfiguration()

    with pytest.raises(ValueError):
        configuration.section("unknown")


def test_unknown_section_cannot_be_set():
    configuration = ApplicationConfiguration()

    with pytest.raises(ValueError):
        configuration.set(
            "unknown",
            "key",
            "value",
        )


def test_set_updates_configuration():
    configuration = ApplicationConfiguration()

    configuration.set(
        "ui",
        "theme",
        "dark",
    )

    assert configuration.get(
        "ui",
        "theme",
    ) == "dark"


def test_set_revalidates_configuration():
    configuration = ApplicationConfiguration()

    with pytest.raises(ValueError):
        configuration.set(
            "ui",
            "theme",
            "invalid",
        )


def test_section_returns_defensive_copy():
    configuration = ApplicationConfiguration()

    section = configuration.section("ui")
    section["theme"] = "dark"

    assert configuration.get(
        "ui",
        "theme",
    ) == "system"


def test_input_is_defensively_copied():
    values = {
        "ui": {
            "theme": "dark",
        }
    }

    configuration = ApplicationConfiguration(values)

    values["ui"]["theme"] = "light"

    assert configuration.get(
        "ui",
        "theme",
    ) == "dark"


def test_to_dict_returns_defensive_copy():
    configuration = ApplicationConfiguration()

    values = configuration.to_dict()

    values["ui"]["theme"] = "dark"

    assert configuration.get(
        "ui",
        "theme",
    ) == "system"


def test_configuration_contains_no_execution_surface():
    configuration = ApplicationConfiguration()

    assert not hasattr(configuration, "execute")
    assert not hasattr(configuration, "diagnose")
    assert not hasattr(configuration, "remediate")
    assert not hasattr(configuration, "authorize")


def test_fleet_configuration_is_ready_for_beta_expansion():
    configuration = ApplicationConfiguration(
        {
            "fleet": {
                "enabled": True,
                "max_machines": 50,
            }
        }
    )

    assert configuration.section("fleet") == {
        "enabled": True,
        "max_machines": 50,
    }


def test_safety_configuration_remains_explicit():
    configuration = ApplicationConfiguration()

    safety = configuration.section("safety")

    assert "require_remediation_authorization" in safety
    assert "allow_automatic_remediation" in safety
