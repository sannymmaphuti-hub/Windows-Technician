"""Production memory-environment compatibility boundary."""

from dataclasses import dataclass
from enum import Enum


class MemoryEnvironmentLevel(str, Enum):
    LOW = "LOW"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MemoryEnvironment:
    total_memory_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.total_memory_bytes, int):
            raise TypeError("total_memory_bytes must be an integer.")

        if isinstance(self.total_memory_bytes, bool):
            raise TypeError("total_memory_bytes must be an integer.")

        if self.total_memory_bytes < 0:
            raise ValueError(
                "total_memory_bytes must not be negative."
            )


@dataclass(frozen=True)
class MemoryCompatibilityResult:
    compatible: bool
    level: MemoryEnvironmentLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.level, MemoryEnvironmentLevel):
            raise TypeError(
                "level must be a MemoryEnvironmentLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


LOW_MEMORY_THRESHOLD_BYTES = 4 * 1024 * 1024 * 1024
HIGH_MEMORY_THRESHOLD_BYTES = 16 * 1024 * 1024 * 1024


def classify_memory_environment(
    environment: MemoryEnvironment,
) -> MemoryEnvironmentLevel:
    """Classify a machine by installed physical memory."""

    if not isinstance(environment, MemoryEnvironment):
        raise TypeError(
            "environment must be a MemoryEnvironment."
        )

    memory = environment.total_memory_bytes

    if memory == 0:
        return MemoryEnvironmentLevel.UNKNOWN

    if memory < LOW_MEMORY_THRESHOLD_BYTES:
        return MemoryEnvironmentLevel.LOW

    if memory >= HIGH_MEMORY_THRESHOLD_BYTES:
        return MemoryEnvironmentLevel.HIGH

    return MemoryEnvironmentLevel.STANDARD


def evaluate_memory_compatibility(
    environment: MemoryEnvironment,
) -> MemoryCompatibilityResult:
    """Evaluate whether a memory environment is supported."""

    level = classify_memory_environment(environment)

    if level is MemoryEnvironmentLevel.UNKNOWN:
        return MemoryCompatibilityResult(
            compatible=False,
            level=level,
            reason="Available system memory could not be determined.",
        )

    if level is MemoryEnvironmentLevel.LOW:
        return MemoryCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "Low-memory environment is supported with "
                "resource-conscious behavior."
            ),
        )

    if level is MemoryEnvironmentLevel.HIGH:
        return MemoryCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "High-memory environment is supported with "
                "full resource capacity."
            ),
        )

    return MemoryCompatibilityResult(
        compatible=True,
        level=level,
        reason="Standard memory environment is supported.",
    )


def memory_compatibility_is_safe(
    environment: MemoryEnvironment,
) -> bool:
    """Return whether the memory environment is safe to operate in."""

    return evaluate_memory_compatibility(environment).compatible
