"""Production display environment compatibility boundary."""

from dataclasses import dataclass
from enum import Enum


class DisplayEnvironmentLevel(str, Enum):
    SMALL = "SMALL"
    STANDARD = "STANDARD"
    LARGE = "LARGE"
    HIGH_DPI = "HIGH_DPI"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class DisplayEnvironment:
    width_pixels: int
    height_pixels: int
    dpi_scale_percent: int

    def __post_init__(self) -> None:
        for name, value in (
            ("width_pixels", self.width_pixels),
            ("height_pixels", self.height_pixels),
            ("dpi_scale_percent", self.dpi_scale_percent),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer.")

            if value < 0:
                raise ValueError(f"{name} must not be negative.")


@dataclass(frozen=True)
class DisplayCompatibilityResult:
    compatible: bool
    levels: tuple[DisplayEnvironmentLevel, ...]
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.levels, tuple):
            raise TypeError("levels must be a tuple.")

        for level in self.levels:
            if not isinstance(level, DisplayEnvironmentLevel):
                raise TypeError(
                    "levels must contain DisplayEnvironmentLevel values."
                )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


MIN_SUPPORTED_WIDTH = 1024
MIN_SUPPORTED_HEIGHT = 600

LARGE_WIDTH = 2560
LARGE_HEIGHT = 1440

HIGH_DPI_THRESHOLD_PERCENT = 150


def classify_display_environment(
    environment: DisplayEnvironment,
) -> tuple[DisplayEnvironmentLevel, ...]:
    """Classify screen dimensions and DPI characteristics."""

    if not isinstance(environment, DisplayEnvironment):
        raise TypeError(
            "environment must be a DisplayEnvironment."
        )

    if (
        environment.width_pixels == 0
        or environment.height_pixels == 0
        or environment.dpi_scale_percent == 0
    ):
        return (DisplayEnvironmentLevel.UNKNOWN,)

    levels: list[DisplayEnvironmentLevel] = []

    if (
        environment.width_pixels < MIN_SUPPORTED_WIDTH
        or environment.height_pixels < MIN_SUPPORTED_HEIGHT
    ):
        levels.append(DisplayEnvironmentLevel.SMALL)
    elif (
        environment.width_pixels >= LARGE_WIDTH
        and environment.height_pixels >= LARGE_HEIGHT
    ):
        levels.append(DisplayEnvironmentLevel.LARGE)
    else:
        levels.append(DisplayEnvironmentLevel.STANDARD)

    if environment.dpi_scale_percent >= HIGH_DPI_THRESHOLD_PERCENT:
        levels.append(DisplayEnvironmentLevel.HIGH_DPI)

    return tuple(levels)


def evaluate_display_compatibility(
    environment: DisplayEnvironment,
) -> DisplayCompatibilityResult:
    """Evaluate whether a display environment is supported."""

    levels = classify_display_environment(environment)

    if DisplayEnvironmentLevel.UNKNOWN in levels:
        return DisplayCompatibilityResult(
            compatible=False,
            levels=levels,
            reason="Display characteristics could not be determined.",
        )

    if DisplayEnvironmentLevel.SMALL in levels:
        return DisplayCompatibilityResult(
            compatible=True,
            levels=levels,
            reason=(
                "Small display is supported with responsive "
                "layout behavior."
            ),
        )

    if DisplayEnvironmentLevel.HIGH_DPI in levels:
        return DisplayCompatibilityResult(
            compatible=True,
            levels=levels,
            reason=(
                "High-DPI display is supported with DPI-aware "
                "layout behavior."
            ),
        )

    return DisplayCompatibilityResult(
        compatible=True,
        levels=levels,
        reason="Display environment is supported.",
    )


def display_compatibility_is_safe(
    environment: DisplayEnvironment,
) -> bool:
    """Return whether the display environment is safe to operate in."""

    return evaluate_display_compatibility(environment).compatible
