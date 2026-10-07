"""Safe production configuration defaults."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SafeDefaults:
    configuration_version: int
    automatic_diagnostics: bool
    remediation_authorized_by_default: bool
    remote_operations_enabled: bool
    telemetry_enabled: bool
    logging_enabled: bool
    ui_theme: str

    def __post_init__(self):
        if not isinstance(
            self.configuration_version,
            int,
        ):
            raise TypeError(
                "configuration_version must be an integer."
            )

        if self.configuration_version <= 0:
            raise ValueError(
                "configuration_version must be positive."
            )

        for field_name in (
            "automatic_diagnostics",
            "remediation_authorized_by_default",
            "remote_operations_enabled",
            "telemetry_enabled",
            "logging_enabled",
        ):
            if not isinstance(
                getattr(self, field_name),
                bool,
            ):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )

        if (
            not isinstance(self.ui_theme, str)
            or not self.ui_theme.strip()
        ):
            raise ValueError(
                "ui_theme must be a non-empty string."
            )


SAFE_DEFAULTS = SafeDefaults(
    configuration_version=1,
    automatic_diagnostics=True,
    remediation_authorized_by_default=False,
    remote_operations_enabled=False,
    telemetry_enabled=False,
    logging_enabled=True,
    ui_theme="system",
)


def safe_default_configuration() -> dict:
    return {
        "version": SAFE_DEFAULTS.configuration_version,
        "diagnostics": {
            "automatic_collection": (
                SAFE_DEFAULTS.automatic_diagnostics
            ),
        },
        "remediation": {
            "authorized_by_default": (
                SAFE_DEFAULTS.remediation_authorized_by_default
            ),
        },
        "remote": {
            "enabled": (
                SAFE_DEFAULTS.remote_operations_enabled
            ),
        },
        "telemetry": {
            "enabled": (
                SAFE_DEFAULTS.telemetry_enabled
            ),
        },
        "logging": {
            "enabled": (
                SAFE_DEFAULTS.logging_enabled
            ),
        },
        "interface": {
            "theme": SAFE_DEFAULTS.ui_theme,
        },
    }


def apply_safe_defaults(
    configuration: dict | None,
) -> dict:
    if configuration is None:
        configuration = {}

    if not isinstance(configuration, dict):
        raise TypeError(
            "configuration must be a dictionary."
        )

    defaults = safe_default_configuration()

    result = dict(defaults)

    for section, values in configuration.items():
        if (
            isinstance(values, dict)
            and isinstance(
                result.get(section),
                dict,
            )
        ):
            merged_section = dict(result[section])
            merged_section.update(values)
            result[section] = merged_section
        else:
            result[section] = values

    return result


def remediation_is_safe_by_default() -> bool:
    return not (
        SAFE_DEFAULTS.remediation_authorized_by_default
    )


def remote_operations_are_disabled_by_default() -> bool:
    return not (
        SAFE_DEFAULTS.remote_operations_enabled
    )


def telemetry_is_disabled_by_default() -> bool:
    return not SAFE_DEFAULTS.telemetry_enabled
