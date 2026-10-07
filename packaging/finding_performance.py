"""Many-findings performance boundaries."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class FindingPerformanceMeasurement:
    operation: str
    finding_count: int
    elapsed_seconds: float

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if not isinstance(self.finding_count, int):
            raise TypeError("finding_count must be an integer.")

        if self.finding_count < 0:
            raise ValueError("finding_count cannot be negative.")

        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative.")

    @property
    def elapsed_milliseconds(self) -> float:
        return self.elapsed_seconds * 1000.0

    @property
    def findings_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return float("inf")

        return self.finding_count / self.elapsed_seconds


@dataclass(frozen=True)
class FindingPerformanceBudget:
    operation: str
    maximum_seconds: float
    minimum_finding_count: int

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.maximum_seconds <= 0:
            raise ValueError("maximum_seconds must be positive.")

        if not isinstance(self.minimum_finding_count, int):
            raise TypeError("minimum_finding_count must be an integer.")

        if self.minimum_finding_count < 0:
            raise ValueError("minimum_finding_count cannot be negative.")

    def accepts(
        self,
        measurement: FindingPerformanceMeasurement,
    ) -> bool:
        if not isinstance(
            measurement,
            FindingPerformanceMeasurement,
        ):
            raise TypeError(
                "measurement must be a FindingPerformanceMeasurement."
            )

        return (
            measurement.operation == self.operation
            and measurement.finding_count >= self.minimum_finding_count
            and measurement.elapsed_seconds <= self.maximum_seconds
        )


def measure_finding_operation(
    operation: str,
    findings: Iterable[T],
    callback: Callable[[list[T]], object],
) -> tuple[object, FindingPerformanceMeasurement]:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not callable(callback):
        raise TypeError("callback must be callable.")

    materialized_findings = list(findings)

    start = perf_counter()

    result = callback(materialized_findings)

    elapsed = perf_counter() - start

    return result, FindingPerformanceMeasurement(
        operation=operation,
        finding_count=len(materialized_findings),
        elapsed_seconds=elapsed,
    )


NORMAL_FINDINGS_BUDGET = FindingPerformanceBudget(
    operation="finding_processing",
    maximum_seconds=0.25,
    minimum_finding_count=100,
)


LARGE_FINDINGS_BUDGET = FindingPerformanceBudget(
    operation="finding_processing",
    maximum_seconds=1.0,
    minimum_finding_count=1000,
)


STRESS_FINDINGS_BUDGET = FindingPerformanceBudget(
    operation="finding_processing",
    maximum_seconds=5.0,
    minimum_finding_count=10000,
)


def finding_processing_is_acceptable(
    measurement: FindingPerformanceMeasurement,
) -> bool:
    if not isinstance(
        measurement,
        FindingPerformanceMeasurement,
    ):
        raise TypeError(
            "measurement must be a FindingPerformanceMeasurement."
        )

    if measurement.finding_count >= 10000:
        return STRESS_FINDINGS_BUDGET.accepts(measurement)

    if measurement.finding_count >= 1000:
        return LARGE_FINDINGS_BUDGET.accepts(measurement)

    return NORMAL_FINDINGS_BUDGET.accepts(measurement)
