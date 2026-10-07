from pathlib import Path
import json

from packaging.configuration_sources import (
    ConfigurationSources,
    build_configuration_locations,
    load_configuration_sources,
)
from packaging.production_configuration import (
    ProductionConfiguration,
    build_production_configuration_from_sources,
)


def test_production_configuration_uses_canonical_sources():
    sources = ConfigurationSources(
        system={
            "logging": True,
            "remote_operations": False,
        },
        user={
            "remote_operations": True,
        },
    )

    result = build_production_configuration_from_sources(
        sources,
    )

    assert isinstance(result, ProductionConfiguration)

    configuration = result.state.configuration

    assert configuration["logging"] is True
    assert configuration["remote_operations"] is True

    assert configuration["version"] == 1
    assert configuration["diagnostics"]["automatic_collection"] is True
    assert configuration["remediation"]["authorized_by_default"] is False
    assert configuration["telemetry"]["enabled"] is False
    assert configuration["interface"]["theme"] == "system"


def test_system_configuration_is_preserved_when_user_has_no_override():
    sources = ConfigurationSources(
        system={
            "logging": True,
            "remote_operations": False,
        },
        user={
            "theme": "dark",
        },
    )

    result = build_production_configuration_from_sources(
        sources,
    )

    configuration = result.state.configuration

    assert configuration["logging"] is True
    assert configuration["remote_operations"] is False
    assert configuration["theme"] == "dark"

    assert configuration["version"] == 1
    assert configuration["diagnostics"]["automatic_collection"] is True
    assert configuration["remediation"]["authorized_by_default"] is False
    assert configuration["telemetry"]["enabled"] is False
    assert configuration["interface"]["theme"] == "system"


def test_safe_defaults_are_applied_after_source_merge():
    sources = ConfigurationSources(
        system={},
        user={},
    )

    result = build_production_configuration_from_sources(
        sources,
    )

    configuration = result.state.configuration

    assert configuration["version"] == 1
    assert configuration["diagnostics"]["automatic_collection"] is True
    assert configuration["remediation"]["authorized_by_default"] is False
    assert configuration["remote"]["enabled"] is False
    assert configuration["telemetry"]["enabled"] is False
    assert configuration["logging"]["enabled"] is True
    assert configuration["interface"]["theme"] == "system"


def test_configuration_files_flow_into_production_configuration(
    tmp_path: Path,
):
    user_root = tmp_path / "user"
    system_root = tmp_path / "system"

    locations = build_configuration_locations(
        user_data_root=user_root,
        system_data_root=system_root,
    )

    locations.user_configuration.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    locations.system_configuration.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    locations.system_configuration.write_text(
        json.dumps(
            {
                "logging": True,
                "remote_operations": False,
            }
        ),
        encoding="utf-8",
    )

    locations.user_configuration.write_text(
        json.dumps(
            {
                "remote_operations": True,
            }
        ),
        encoding="utf-8",
    )

    sources = load_configuration_sources(locations)

    result = build_production_configuration_from_sources(
        sources,
    )

    configuration = result.state.configuration

    assert configuration["logging"] is True
    assert configuration["remote_operations"] is True

    assert configuration["version"] == 1
    assert configuration["diagnostics"]["automatic_collection"] is True
    assert configuration["remediation"]["authorized_by_default"] is False
    assert configuration["telemetry"]["enabled"] is False
    assert configuration["interface"]["theme"] == "system"


def test_runtime_paths_and_configuration_sources_remain_distinct(
    tmp_path: Path,
):
    user_root = tmp_path / "user"
    system_root = tmp_path / "system"

    locations = build_configuration_locations(
        user_data_root=user_root,
        system_data_root=system_root,
    )

    assert locations.user_configuration != locations.system_configuration
    assert locations.user_configuration.parent == user_root / "config"
    assert locations.system_configuration.parent == system_root / "config"
