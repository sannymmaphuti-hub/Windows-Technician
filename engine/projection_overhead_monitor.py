"""Performance measurements for read-only system projections."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import perf_counter
from typing import Any, Callable

from engine.diagnostic_performance_profiler import (
    DiagnosticPerformanceProfiler,
)


@dataclass(frozen=True, slots=True)
class ProjectionMeasurement:
    projection_name: str
    duration_seconds: float
    succeeded: bool

    def projection(self) -> dict[str, Any]:
        return {
            "projection_name": self.projection_name,
            "duration_seconds": self.duration_seconds,
            "succeeded": self.succeeded,
        }


class ProjectionOverheadMonitor:
    """Measure projection calls without caching or mutating their providers."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, *, history_capacity: int = 1000) -> None:
        self._profiler = DiagnosticPerformanceProfiler(
            history_capacity=history_capacity
        )
        self._lock = RLock()
        self._measurements: list[ProjectionMeasurement] = []
        self._capacity = history_capacity
        self._evicted_count = 0

    def measure(
        self,
        projection_name: str,
        callback: Callable[[], Any],
    ) -> Any:
        if not isinstance(projection_name, str) or not projection_name.strip():
            raise ValueError("projection_name must be a non-empty string")
        if not callable(callback):
            raise TypeError("callback must be callable")

        started = perf_counter()
        succeeded = False

        try:
            result = callback()
            succeeded = True
            return result
        finally:
            duration = perf_counter() - started
            self._profiler.record(projection_name, duration)
            measurement = ProjectionMeasurement(
                projection_name=projection_name,
                duration_seconds=duration,
                succeeded=succeeded,
            )

            with self._lock:
                if len(self._measurements) >= self._capacity:
                    self._measurements.pop(0)
                    self._evicted_count += 1
                self._measurements.append(measurement)

    def projection(self) -> dict[str, Any]:
        with self._lock:
            measurements = [
                item.projection() for item in self._measurements
            ]
            evicted_count = self._evicted_count

        return {
            "schema_version": self.SCHEMA_VERSION,
            "measurement_count": len(measurements),
            "evicted_count": evicted_count,
            "measurements": measurements,
            "duration_summary": self._profiler.projection()["summary"],
            "caching_enabled": False,
            "provider_mutation_performed": False,
        }
