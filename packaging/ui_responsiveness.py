"""UI responsiveness performance boundaries."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class UIResponsivenessMeasurement:
    operation: str
    elapsed_seconds: float
    completed: bool

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative.")

        if not isinstance(self.completed, bool):
            raise TypeError("completed must be a boolean.")

    @property
    def elapsed_milliseconds(self) -> float:
        return self.elapsed_seconds * 1000.0


@dataclass(frozen=True)
class UIResponsivenessBudget:
    operation: str
    maximum_seconds: float

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.maximum_seconds <= 0:
            raise ValueError("maximum_seconds must be positive.")

    def accepts(
        self,
        measurement: UIResponsivenessMeasurement,
    ) -> bool:
        if not isinstance(
            measurement,
            UIResponsivenessMeasurement,
        ):
            raise TypeError(
                "measurement must be a UIResponsivenessMeasurement."
            )

        return (
            measurement.operation == self.operation
            and measurement.completed
            and measurement.elapsed_seconds <= self.maximum_seconds
        )


def measure_ui_operation(
    operation: str,
    callback: Callable[[], T],
) -> tuple[T, UIResponsivenessMeasurement]:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not callable(callback):
        raise TypeError("callback must be callable.")

    start = perf_counter()

    try:
        result = callback()
        completed = True
        return_value = result
    except Exception:
        completed = False
        raise
    finally:
        elapsed = perf_counter() - start

        measurement = UIResponsivenessMeasurement(
            operation=operation,
            elapsed_seconds=elapsed,
            completed=completed,
        )

    if not completed:
        raise RuntimeError("UI operation did not complete.")

    return return_value, measurement


UI_INTERACTION_PERFORMANCE_BUDGET = UIResponsivenessBudget(
    operation="ui_interaction",
    maximum_seconds=0.1,
)


UI_STATE_UPDATE_PERFORMANCE_BUDGET = UIResponsivenessBudget(
    operation="ui_state_update",
    maximum_seconds=0.1,
)


DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET = UIResponsivenessBudget(
    operation="dashboard_refresh",
    maximum_seconds=0.25,
)


def ui_interaction_is_responsive(
    measurement: UIResponsivenessMeasurement,
) -> bool:
    return UI_INTERACTION_PERFORMANCE_BUDGET.accepts(measurement)


def ui_state_update_is_responsive(
    measurement: UIResponsivenessMeasurement,
) -> bool:
    return UI_STATE_UPDATE_PERFORMANCE_BUDGET.accepts(measurement)


def dashboard_refresh_is_responsive(
    measurement: UIResponsivenessMeasurement,
) -> bool:
    return DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET.accepts(measurement)
