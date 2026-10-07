"""Windows Technician production packaging metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationMetadata:
    """Canonical identity and release metadata for the application."""

    name: str
    display_name: str
    version: str
    release_channel: str
    executable_name: str
    package_name: str

    def __post_init__(self):
        values = {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "release_channel": self.release_channel,
            "executable_name": self.executable_name,
            "package_name": self.package_name,
        }

        for field_name, value in values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not self.version.startswith("0.9."):
            raise ValueError(
                "Windows Technician packaging metadata must target v0.9."
            )

    @property
    def version_tuple(self):
        """Return the numeric version components."""
        return tuple(int(part) for part in self.version.split("."))

    @property
    def full_display_name(self):
        """Return the user-facing application identity."""
        return f"{self.display_name} {self.version}"


APPLICATION_METADATA = ApplicationMetadata(
    name="windows-technician",
    display_name="Windows Technician",
    version="0.9.0",
    release_channel="beta",
    executable_name="WindowsTechnician.exe",
    package_name="WindowsTechnician",
)
