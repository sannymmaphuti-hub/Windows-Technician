from copy import deepcopy

from packaging.application_metadata import APPLICATION_METADATA


class ApplicationState:
    """
    Canonical application-level state for Windows Technician.

    This object represents application state only.
    It does not perform diagnostics, remediation, execution,
    networking, or UI operations.
    """

    _STATUSES = {
        "STARTING",
        "READY",
        "BUSY",
        "ERROR",
        "STOPPING",
        "STOPPED",
    }

    def __init__(
        self,
        application_name="Windows Technician",
        version=APPLICATION_METADATA.version,
        status="STARTING",
        configuration=None,
        active_case_id=None,
        active_machine_id=None,
    ):
        if not isinstance(application_name, str):
            raise ValueError(
                "application_name must be a non-empty string."
            )

        application_name = application_name.strip()

        if not application_name:
            raise ValueError(
                "application_name must be a non-empty string."
            )

        if not isinstance(version, str):
            raise ValueError(
                "version must be a non-empty string."
            )

        version = version.strip()

        if not version:
            raise ValueError(
                "version must be a non-empty string."
            )

        self.application_name = application_name
        self.version = version

        self.status = self._normalize_status(status)

        self.configuration = deepcopy(
            configuration
            if isinstance(configuration, dict)
            else {}
        )

        self.active_case_id = self._normalize_optional_identifier(
            active_case_id
        )

        self.active_machine_id = (
            self._normalize_optional_identifier(
                active_machine_id
            )
        )

    @classmethod
    def _normalize_status(cls, status):
        if not isinstance(status, str):
            raise ValueError(
                "status must be a supported string value."
            )

        normalized = status.strip().upper()

        if normalized not in cls._STATUSES:
            raise ValueError(
                f"Unsupported status: {status!r}."
            )

        return normalized

    @staticmethod
    def _normalize_optional_identifier(value):
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "identifier must be a string or None."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "identifier must be a non-empty string "
                "when supplied."
            )

        return normalized.upper()

    def set_status(self, status):
        self.status = self._normalize_status(status)

    def set_active_case(self, case_id):
        self.active_case_id = (
            self._normalize_optional_identifier(
                case_id
            )
        )

    def set_active_machine(self, machine_id):
        self.active_machine_id = (
            self._normalize_optional_identifier(
                machine_id
            )
        )

    def clear_active_context(self):
        self.active_case_id = None
        self.active_machine_id = None

    def to_dict(self):
        return {
            "application_name": self.application_name,
            "version": self.version,
            "status": self.status,
            "configuration": deepcopy(
                self.configuration
            ),
            "active_case_id": self.active_case_id,
            "active_machine_id": self.active_machine_id,
        }
