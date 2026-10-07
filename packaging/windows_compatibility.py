"""Production Windows compatibility boundary."""

from dataclasses import dataclass
from enum import Enum

from packaging.windows_environment import WindowsEnvironment


class WindowsSupportLevel(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class WindowsCompatibilityResult:
    supported: bool
    support_level: WindowsSupportLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.supported, bool):
            raise TypeError("supported must be a boolean.")

        if not isinstance(self.support_level, WindowsSupportLevel):
            raise TypeError(
                "support_level must be a WindowsSupportLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


SUPPORTED_MAJOR_VERSIONS = frozenset({10, 11})


def _major_windows_version(
    operating_system_version: str,
) -> int | None:
    """Extract the major Windows version from the canonical version string."""

    if not isinstance(operating_system_version, str):
        return None

    value = operating_system_version.strip()

    if not value:
        return None

    major_text = value.split(".", 1)[0]

    try:
        return int(major_text)
    except ValueError:
        return None


def evaluate_windows_compatibility(
    environment: WindowsEnvironment,
) -> WindowsCompatibilityResult:
    """Evaluate whether a Windows environment is supported."""

    if not isinstance(environment, WindowsEnvironment):
        raise TypeError(
            "environment must be a WindowsEnvironment."
        )

    major_version = _major_windows_version(
        environment.operating_system_version
    )

    if major_version is None:
        return WindowsCompatibilityResult(
            supported=False,
            support_level=WindowsSupportLevel.UNKNOWN,
            reason=(
                "The Windows operating system version could not "
                "be determined."
            ),
        )

    if major_version in SUPPORTED_MAJOR_VERSIONS:
        return WindowsCompatibilityResult(
            supported=True,
            support_level=WindowsSupportLevel.SUPPORTED,
            reason=f"Windows {major_version} is supported.",
        )

    return WindowsCompatibilityResult(
        supported=False,
        support_level=WindowsSupportLevel.UNSUPPORTED,
        reason=f"Windows {major_version} is not supported.",
    )


def windows_compatibility_is_safe(
    environment: WindowsEnvironment,
) -> bool:
    """Return whether the environment is within the supported boundary."""

    result = evaluate_windows_compatibility(environment)
    return result.supported
