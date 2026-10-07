"""Large diagnostic dataset performance boundaries."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class DatasetPerformanceMeasurement:
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


@dataclass(frozen=True)
class DatasetPerformanceBudget:
    operation: str
    maximum_seconds: float
    minimum_item_count: int

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.maximum_seconds <= 0:
            raise ValueError("maximum_seconds must be positive.")

        if not isinstance(self.minimum_item_count, int):
            raise TypeError("minimum_item_count must be an integer.")

        if self.minimum_item_count < 0:
            raise ValueError("minimum_item_count cannot be negative.")

    def accepts(
        self,
        measurement: DatasetPerformanceMeasurement,
    ) -> bool:
        if not isinstance(
            measurement,
            DatasetPerformanceMeasurement,
        ):
            raise TypeError(
                "measurement must be a DatasetPerformanceMeasurement."
            )

        return (
            measurement.operation == self.operation
            and measurement.item_count >= self.minimum_item_count
            and measurement.elapsed_seconds <= self.maximum_seconds
        )


def measure_dataset_operation(
    operation: str,
    dataset: Iterable[T],
    callback: Callable[[list[T]], object],
) -> tuple[object, DatasetPerformanceMeasurement]:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not callable(callback):
        raise TypeError("callback must be callable.")

    items = list(dataset)

    start = perf_counter()

    result = callback(items)

    elapsed = perf_counter() - start

    return result, DatasetPerformanceMeasurement(
        operation=operation,
        item_count=len(items),
        elapsed_seconds=elapsed,
    )


NORMAL_DATASET_BUDGET = DatasetPerformanceBudget(
    operation="diagnostic_dataset_processing",
    maximum_seconds=0.25,
    minimum_item_count=100,
)


LARGE_DATASET_BUDGET = DatasetPerformanceBudget(
    operation="diagnostic_dataset_processing",
    maximum_seconds=1.0,
    minimum_item_count=1000,
)


STRESS_DATASET_BUDGET = DatasetPerformanceBudget(
    operation="diagnostic_dataset_processing",
    maximum_seconds=5.0,
    minimum_item_count=10000,
)


def diagnostic_dataset_is_acceptable(
    measurement: DatasetPerformanceMeasurement,
) -> bool:
    if not isinstance(
        measurement,
        DatasetPerformanceMeasurement,
    ):
        raise TypeError(
            "measurement must be a DatasetPerformanceMeasurement."
        )

    if measurement.item_count >= 10000:
        return STRESS_DATASET_BUDGET.accepts(measurement)

    if measurement.item_count >= 1000:
        return LARGE_DATASET_BUDGET.accepts(measurement)

    return NORMAL_DATASET_BUDGET.accepts(measurement)
