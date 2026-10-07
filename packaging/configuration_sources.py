"""User and system configuration boundary."""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ConfigurationLocations:
    user_configuration: Path
    system_configuration: Path

    def __post_init__(self):
        if not isinstance(
            self.user_configuration,
            Path,
        ):
            raise TypeError(
                "user_configuration must be a Path."
            )

        if not isinstance(
            self.system_configuration,
            Path,
        ):
            raise TypeError(
                "system_configuration must be a Path."
            )


@dataclass(frozen=True)
class ConfigurationSources:
    user: dict
    system: dict

    def __post_init__(self):
        if not isinstance(self.user, dict):
            raise TypeError(
                "user configuration must be a dictionary."
            )

        if not isinstance(self.system, dict):
            raise TypeError(
                "system configuration must be a dictionary."
            )


def build_configuration_locations(
    *,
    user_data_root: Path,
    system_data_root: Path,
) -> ConfigurationLocations:
    if not isinstance(user_data_root, Path):
        raise TypeError(
            "user_data_root must be a Path."
        )

    if not isinstance(system_data_root, Path):
        raise TypeError(
            "system_data_root must be a Path."
        )

    return ConfigurationLocations(
        user_configuration=(
            user_data_root
            / "config"
            / "settings.json"
        ),
        system_configuration=(
            system_data_root
            / "config"
            / "system.json"
        ),
    )


def load_configuration_file(
    path: Path,
) -> dict:
    if not isinstance(path, Path):
        raise TypeError(
            "path must be a Path."
        )

    if not path.exists():
        return {}

    if not path.is_file():
        raise ValueError(
            "configuration path must be a file."
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        value = json.load(handle)

    if not isinstance(value, dict):
        raise ValueError(
            "configuration file must contain an object."
        )

    return value


def load_configuration_sources(
    locations: ConfigurationLocations,
) -> ConfigurationSources:
    if not isinstance(
        locations,
        ConfigurationLocations,
    ):
        raise TypeError(
            "locations must be ConfigurationLocations."
        )

    return ConfigurationSources(
        user=load_configuration_file(
            locations.user_configuration
        ),
        system=load_configuration_file(
            locations.system_configuration
        ),
    )


def merge_configuration(
    sources: ConfigurationSources,
) -> dict:
    if not isinstance(
        sources,
        ConfigurationSources,
    ):
        raise TypeError(
            "sources must be ConfigurationSources."
        )

    merged = dict(sources.system)
    merged.update(sources.user)

    return merged


def user_configuration_overrides_system(
    sources: ConfigurationSources,
    key: str,
) -> bool:
    if not isinstance(
        sources,
        ConfigurationSources,
    ):
        raise TypeError(
            "sources must be ConfigurationSources."
        )

    if not isinstance(key, str) or not key.strip():
        raise ValueError(
            "key must be a non-empty string."
        )

    return (
        key in sources.user
        and key in sources.system
        and sources.user[key] != sources.system[key]
    )
