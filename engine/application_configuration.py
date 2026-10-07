from copy import deepcopy


class ApplicationConfiguration:
    """
    Canonical configuration for the Windows Technician
    beta application.

    Configuration describes application behaviour and
    preferences. It does not perform application actions.
    """

    DEFAULTS = {
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

    def __init__(self, values=None):
        self._values = deepcopy(self.DEFAULTS)

        if values is not None:
            if not isinstance(values, dict):
                raise ValueError(
                    "Configuration values must be a dictionary."
                )

            self._merge(
                self._values,
                values,
            )

        self._validate()

    @classmethod
    def _merge(cls, target, source):
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                cls._merge(target[key], value)
            else:
                target[key] = deepcopy(value)

    def _validate(self):
        ui = self._values["ui"]
        diagnostics = self._values["diagnostics"]
        fleet = self._values["fleet"]
        safety = self._values["safety"]

        if ui["theme"] not in {
            "system",
            "light",
            "dark",
        }:
            raise ValueError(
                "Unsupported UI theme."
            )

        if not isinstance(
            ui["compact_mode"],
            bool,
        ):
            raise ValueError(
                "compact_mode must be boolean."
            )

        if not isinstance(
            diagnostics["enabled"],
            bool,
        ):
            raise ValueError(
                "diagnostics.enabled must be boolean."
            )

        if not isinstance(
            diagnostics["collect_system_information"],
            bool,
        ):
            raise ValueError(
                "diagnostics.collect_system_information "
                "must be boolean."
            )

        if not isinstance(
            fleet["enabled"],
            bool,
        ):
            raise ValueError(
                "fleet.enabled must be boolean."
            )

        if (
            not isinstance(
                fleet["max_machines"],
                int,
            )
            or isinstance(
                fleet["max_machines"],
                bool,
            )
            or fleet["max_machines"] < 1
        ):
            raise ValueError(
                "fleet.max_machines must be a positive integer."
            )

        if not isinstance(
            safety["require_remediation_authorization"],
            bool,
        ):
            raise ValueError(
                "safety.require_remediation_authorization "
                "must be boolean."
            )

        if not isinstance(
            safety["allow_automatic_remediation"],
            bool,
        ):
            raise ValueError(
                "safety.allow_automatic_remediation "
                "must be boolean."
            )

        if (
            safety["allow_automatic_remediation"]
            and not safety["require_remediation_authorization"]
        ):
            raise ValueError(
                "Automatic remediation cannot be enabled "
                "without remediation authorization."
            )

    def get(self, section, key, default=None):
        section_values = self._values.get(section)

        if not isinstance(section_values, dict):
            return default

        return deepcopy(
            section_values.get(key, default)
        )

    def set(self, section, key, value):
        if section not in self._values:
            raise ValueError(
                f"Unknown configuration section: {section!r}."
            )

        if not isinstance(
            self._values[section],
            dict,
        ):
            raise ValueError(
                f"Configuration section is invalid: {section!r}."
            )

        updated = deepcopy(self._values)

        updated[section][key] = deepcopy(value)

        candidate = ApplicationConfiguration(
            updated
        )

        self._values = candidate.to_dict()

    def section(self, section):
        if section not in self._values:
            raise ValueError(
                f"Unknown configuration section: {section!r}."
            )

        return deepcopy(
            self._values[section]
        )

    def to_dict(self):
        return deepcopy(self._values)
