"""Configuration loading and recovery boundary."""

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ConfigurationRecovery:
    configuration: dict
    recovered: bool
    source: str
    quarantined_path: Path | None = None


def default_configuration() -> dict:
    return {
        "version": 1,
        "diagnostics": {
            "automatic_collection": True,
        },
        "interface": {
            "theme": "system",
        },
    }


def _quarantine_path(configuration_path: Path) -> Path:
    base = configuration_path.with_suffix(
        configuration_path.suffix + ".corrupt"
    )

    if not base.exists():
        return base

    counter = 1

    while True:
        candidate = configuration_path.with_suffix(
            configuration_path.suffix + f".corrupt.{counter}"
        )

        if not candidate.exists():
            return candidate

        counter += 1


def load_configuration(
    configuration_path: Path,
) -> ConfigurationRecovery:
    if not isinstance(configuration_path, Path):
        raise TypeError(
            "configuration_path must be a Path."
        )

    if not configuration_path.exists():
        return ConfigurationRecovery(
            configuration=default_configuration(),
            recovered=True,
            source="defaults",
        )

    if not configuration_path.is_file():
        raise ValueError(
            "configuration_path must point to a file."
        )

    try:
        with configuration_path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            configuration = json.load(handle)
    except (OSError, json.JSONDecodeError):
        quarantine = _quarantine_path(configuration_path)
        configuration_path.replace(quarantine)

        return ConfigurationRecovery(
            configuration=default_configuration(),
            recovered=True,
            source="recovered",
            quarantined_path=quarantine,
        )

    if not isinstance(configuration, dict):
        quarantine = _quarantine_path(configuration_path)
        configuration_path.replace(quarantine)

        return ConfigurationRecovery(
            configuration=default_configuration(),
            recovered=True,
            source="recovered",
            quarantined_path=quarantine,
        )

    return ConfigurationRecovery(
        configuration=configuration,
        recovered=False,
        source="file",
    )


def save_configuration(
    configuration_path: Path,
    configuration: dict,
) -> None:
    if not isinstance(configuration_path, Path):
        raise TypeError(
            "configuration_path must be a Path."
        )

    if not isinstance(configuration, dict):
        raise TypeError(
            "configuration must be a dictionary."
        )

    configuration_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with configuration_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            configuration,
            handle,
            indent=2,
            sort_keys=True,
        )
