"""Performance and scale policy boundary for Windows Technician."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PerformanceLimits:
    """Explicit resource budgets for workload admission."""

    max_concurrent_diagnostics: int = 8
    max_managed_machines: int = 500
    max_events_retained: int = 10_000
    max_projection_items: int = 1_000

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be at least 1")


@dataclass(frozen=True, slots=True)
class CapacityDecision:
    """Read-only result of evaluating a workload against a budget."""

    admitted: bool
    requested: int
    available: int
    reason: str

    def projection(self) -> dict[str, Any]:
        return asdict(self)


class PerformanceScaleBoundary:
    """Evaluates resource budgets without executing any workload."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        limits: PerformanceLimits | None = None,
    ) -> None:
        self._limits = limits or PerformanceLimits()

    @property
    def limits(self) -> PerformanceLimits:
        return self._limits

    def evaluate_capacity(
        self,
        *,
        resource: str,
        requested: int,
        current: int = 0,
    ) -> CapacityDecision:
        """Determine whether a workload fits within a supported budget."""

        if resource not in {
            "concurrent_diagnostics",
            "managed_machines",
            "retained_events",
            "projection_items",
        }:
            raise ValueError(f"Unsupported resource: {resource}")

        for name, value in (
            ("requested", requested),
            ("current", current),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

        limit_name = {
            "concurrent_diagnostics": "max_concurrent_diagnostics",
            "managed_machines": "max_managed_machines",
            "retained_events": "max_events_retained",
            "projection_items": "max_projection_items",
        }[resource]

        limit = getattr(self._limits, limit_name)
        available = max(0, limit - current)
        admitted = requested <= available

        if admitted:
            reason = "WITHIN_CAPACITY"
        elif current >= limit:
            reason = "CAPACITY_EXHAUSTED"
        else:
            reason = "REQUEST_EXCEEDS_AVAILABLE_CAPACITY"

        return CapacityDecision(
            admitted=admitted,
            requested=requested,
            available=available,
            reason=reason,
        )

    def projection(self) -> dict[str, Any]:
        """Return a detached description of the configured budgets."""

        return {
            "schema_version": self.SCHEMA_VERSION,
            "limits": asdict(self._limits),
            "execution_performed": False,
        }
