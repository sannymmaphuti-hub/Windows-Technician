"""Dashboard and rendering performance boundaries."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RenderingPerformanceBudget:
    operation: str
    maximum_seconds: float

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.maximum_seconds <= 0:
            raise ValueError("maximum_seconds must be positive.")

    def accepts(self, elapsed_seconds: float) -> bool:
        if not isinstance(elapsed_seconds, (int, float)):
            raise TypeError("elapsed_seconds must be numeric.")

        if elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative.")

        return elapsed_seconds <= self.maximum_seconds


@dataclass(frozen=True)
class RenderingPerformanceMeasurement:
    operation: str
    item_count: int
    elapsed_seconds: float

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if not isinstance(self.item_count, int):
            raise TypeError("item_count must be an integer.")

        if self.item_count < 0:
            raise ValueError("item_count cannot be negative.")

        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative.")

    @property
    def elapsed_milliseconds(self) -> float:
        return self.elapsed_seconds * 1000.0

    @property
    def items_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return float("inf")

        return self.item_count / self.elapsed_seconds


def measure_rendering_operation(
    operation: str,
    item_count: int,
    callback: Callable[[], T],
) -> tuple[T, RenderingPerformanceMeasurement]:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not isinstance(item_count, int):
        raise TypeError("item_count must be an integer.")

    if item_count < 0:
        raise ValueError("item_count cannot be negative.")

    if not callable(callback):
        raise TypeError("callback must be callable.")

    start = perf_counter()

    result = callback()

    elapsed = perf_counter() - start

    return result, RenderingPerformanceMeasurement(
        operation=operation,
        item_count=item_count,
        elapsed_seconds=elapsed,
    )


DASHBOARD_RENDERING_PERFORMANCE_BUDGET = RenderingPerformanceBudget(
    operation="dashboard_rendering",
    maximum_seconds=1.0,
)


LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET = RenderingPerformanceBudget(
    operation="large_dashboard_rendering",
    maximum_seconds=2.0,
)


def dashboard_rendering_is_acceptable(
    elapsed_seconds: float,
) -> bool:
    return DASHBOARD_RENDERING_PERFORMANCE_BUDGET.accepts(
        elapsed_seconds
    )


def large_dashboard_rendering_is_acceptable(
    elapsed_seconds: float,
) -> bool:
    return LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET.accepts(
        elapsed_seconds
    )
