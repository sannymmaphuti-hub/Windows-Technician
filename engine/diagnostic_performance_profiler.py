"""Diagnostic pipeline performance measurement primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import median
from threading import RLock
from time import perf_counter
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class PerformanceSample:
    operation: str
    duration_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string")
        if (
            isinstance(self.duration_seconds, bool)
            or not isinstance(self.duration_seconds, (int, float))
            or not isfinite(self.duration_seconds)
            or self.duration_seconds < 0
        ):
            raise ValueError("duration_seconds must be finite and non-negative")

    def projection(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "duration_seconds": float(self.duration_seconds),
        }


class DiagnosticPerformanceProfiler:
    """Measure supplied callables without managing diagnostic execution."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, *, history_capacity: int = 1000) -> None:
        if (
            isinstance(history_capacity, bool)
            or not isinstance(history_capacity, int)
        ):
            raise TypeError("history_capacity must be an integer")
        if history_capacity < 1:
            raise ValueError("history_capacity must be positive")

        self._capacity = history_capacity
        self._samples: list[PerformanceSample] = []
        self._evicted_count = 0
        self._lock = RLock()

    def measure(self, operation: str, callback: Callable[[], Any]) -> Any:
        """Return the callback result, recording elapsed time even on failure."""
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string")
        if not callable(callback):
            raise TypeError("callback must be callable")

        started = perf_counter()
        try:
            return callback()
        finally:
            elapsed = perf_counter() - started
            self.record(operation, elapsed)

    def record(self, operation: str, duration_seconds: float) -> PerformanceSample:
        sample = PerformanceSample(operation, duration_seconds)

        with self._lock:
            if len(self._samples) >= self._capacity:
                self._samples.pop(0)
                self._evicted_count += 1
            self._samples.append(sample)

        return sample

    def projection(self) -> dict[str, Any]:
        with self._lock:
            samples = [sample.projection() for sample in self._samples]
            evicted_count = self._evicted_count
            capacity = self._capacity

        durations = [sample["duration_seconds"] for sample in samples]
        summary = {
            "sample_count": len(durations),
            "minimum_seconds": min(durations) if durations else None,
            "median_seconds": median(durations) if durations else None,
            "maximum_seconds": max(durations) if durations else None,
        }

        return {
            "schema_version": self.SCHEMA_VERSION,
            "capacity": capacity,
            "evicted_count": evicted_count,
            "samples": samples,
            "summary": summary,
            "execution_performed_by_profiler": False,
        }
