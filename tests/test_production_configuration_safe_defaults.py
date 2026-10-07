from pathlib import Path

from packaging.configuration_environment_architecture import (
    build_configuration_environment_architecture,
)
from packaging.configuration_sources import ConfigurationSources
from packaging.production_configuration import (
    ProductionConfiguration,
    build_default_production_configuration,
    build_production_configuration_from_environment,
    build_production_configuration_from_sources,
)
from packaging.safe_defaults import safe_default_configuration


def test_missing_configuration_receives_safe_defaults():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={},
        )
    )

    defaults = safe_default_configuration()

    assert result.state.configuration == defaults


def test_missing_remediation_authorization_is_safe():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={},
        )
    )

    assert (
        result.state.configuration["remediation"][
            "authorized_by_default"
        ]
        is False
    )


def test_missing_remote_operations_are_disabled():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={},
        )
    )

    assert (
        result.state.configuration["remote"]["enabled"]
        is False
    )


def test_missing_telemetry_is_disabled():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={},
        )
    )

    assert (
        result.state.configuration["telemetry"]["enabled"]
        is False
    )


def test_user_configuration_can_override_safe_default():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={
                "interface": {
                    "theme": "dark",
                },
            },
        )
    )

    assert (
        result.state.configuration["interface"]["theme"]
        == "dark"
    )


def test_existing_effective_configuration_is_preserved():
    architecture = build_configuration_environment_architecture(
        project_root=Path("."),
        user_data_root=Path(".test-user"),
        system_data_root=Path(".test-system"),
    )

    result = build_production_configuration_from_environment(
        architecture,
    )

    assert (
        result.state.configuration
        == architecture.effective_configuration
    )


def test_environment_architecture_produces_safe_production_configuration():
    architecture = build_configuration_environment_architecture(
        project_root=Path("."),
        user_data_root=Path(".test-user"),
        system_data_root=Path(".test-system"),
    )

    result = build_production_configuration_from_environment(
        architecture,
    )

    assert isinstance(result, ProductionConfiguration)
    assert result.state.safe is True


def test_recovery_state_is_preserved():
    result = build_production_configuration_from_sources(
        ConfigurationSources(
            system={},
            user={},
        ),
        recovered=True,
    )

    assert result.state.recovered is True


def test_default_production_configuration_uses_canonical_environment(
    tmp_path: Path,
):
    result = build_default_production_configuration(
        project_root=tmp_path / "project",
        user_data_root=tmp_path / "user",
        system_data_root=tmp_path / "system",
    )

    assert isinstance(result, ProductionConfiguration)
    assert result.state.safe is True
    assert (
        result.state.configuration["remote"]["enabled"]
        is False
    )
