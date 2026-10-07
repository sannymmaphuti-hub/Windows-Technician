"""Production performance measurement boundaries."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class PerformanceMeasurement:
    operation: str
    elapsed_seconds: float

    def __post_init__(self):
        if (
            not isinstance(self.operation, str)
            or not self.operation.strip()
        ):
            raise ValueError(
                "operation must be a non-empty string."
            )

        if self.elapsed_seconds < 0:
            raise ValueError(
                "elapsed_seconds cannot be negative."
            )

    @property
    def elapsed_milliseconds(self) -> float:
        return self.elapsed_seconds * 1000.0


@dataclass(frozen=True)
class PerformanceBudget:
    operation: str
    maximum_seconds: float

    def __post_init__(self):
        if (
            not isinstance(self.operation, str)
            or not self.operation.strip()
        ):
            raise ValueError(
                "operation must be a non-empty string."
            )

        if self.maximum_seconds <= 0:
            raise ValueError(
                "maximum_seconds must be positive."
            )

    def accepts(
        self,
        measurement: PerformanceMeasurement,
    ) -> bool:
        if not isinstance(
            measurement,
            PerformanceMeasurement,
        ):
            raise TypeError(
                "measurement must be a PerformanceMeasurement."
            )

        return (
            measurement.operation == self.operation
            and measurement.elapsed_seconds
            <= self.maximum_seconds
        )


def measure_operation(
    operation: str,
    callback: Callable[[], T],
) -> tuple[T, PerformanceMeasurement]:
    if (
        not isinstance(operation, str)
        or not operation.strip()
    ):
        raise ValueError(
            "operation must be a non-empty string."
        )

    if not callable(callback):
        raise TypeError(
            "callback must be callable."
        )

    start = perf_counter()

    result = callback()

    elapsed = perf_counter() - start

    return result, PerformanceMeasurement(
        operation=operation,
        elapsed_seconds=elapsed,
    )


STARTUP_PERFORMANCE_BUDGET = PerformanceBudget(
    operation="application_startup",
    maximum_seconds=5.0,
)


def startup_performance_is_acceptable(
    measurement: PerformanceMeasurement,
) -> bool:
    return STARTUP_PERFORMANCE_BUDGET.accepts(
        measurement
    )
