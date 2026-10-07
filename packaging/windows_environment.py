"""Windows runtime compatibility boundary."""

from dataclasses import dataclass
import platform
import sys

from packaging.application_metadata import APPLICATION_METADATA


@dataclass(frozen=True)
class WindowsEnvironment:
    operating_system: str
    operating_system_version: str
    windows_build: str
    architecture: str
    python_version: str
    application_version: str

    @property
    def is_windows(self) -> bool:
        return self.operating_system.lower() == "windows"

    @property
    def supports_application(self) -> bool:
        return (
            self.is_windows
            and self.architecture in {
                "AMD64",
                "ARM64",
                "x86",
            }
        )


def detect_windows_environment() -> WindowsEnvironment:
    operating_system = platform.system()

    return WindowsEnvironment(
        operating_system=operating_system,
        operating_system_version=platform.version(),
        windows_build=platform.release(),
        architecture=platform.machine(),
        python_version=platform.python_version(),
        application_version=APPLICATION_METADATA.version,
    )


def environment_is_supported(
    environment: WindowsEnvironment,
) -> bool:
    if not isinstance(
        environment,
        WindowsEnvironment,
    ):
        raise TypeError(
            "environment must be a WindowsEnvironment."
        )

    return environment.supports_application
