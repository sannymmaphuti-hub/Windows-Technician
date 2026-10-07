"""Memory and resource pressure performance boundaries."""

from dataclasses import dataclass
from typing import Callable, TypeVar
import os
import time


T = TypeVar("T")


@dataclass(frozen=True)
class ResourceMeasurement:
    operation: str
    elapsed_seconds: float
    memory_before_bytes: int
    memory_after_bytes: int

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative.")

        if not isinstance(self.memory_before_bytes, int):
            raise TypeError("memory_before_bytes must be an integer.")

        if not isinstance(self.memory_after_bytes, int):
            raise TypeError("memory_after_bytes must be an integer.")

        if self.memory_before_bytes < 0:
            raise ValueError("memory_before_bytes cannot be negative.")

        if self.memory_after_bytes < 0:
            raise ValueError("memory_after_bytes cannot be negative.")

    @property
    def memory_growth_bytes(self) -> int:
        return self.memory_after_bytes - self.memory_before_bytes

    @property
    def memory_growth_megabytes(self) -> float:
        return self.memory_growth_bytes / (1024 * 1024)


@dataclass(frozen=True)
class ResourcePerformanceBudget:
    operation: str
    maximum_seconds: float
    maximum_memory_growth_bytes: int

    def __post_init__(self):
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ValueError("operation must be a non-empty string.")

        if self.maximum_seconds <= 0:
            raise ValueError("maximum_seconds must be positive.")

        if not isinstance(self.maximum_memory_growth_bytes, int):
            raise TypeError(
                "maximum_memory_growth_bytes must be an integer."
            )

        if self.maximum_memory_growth_bytes < 0:
            raise ValueError(
                "maximum_memory_growth_bytes cannot be negative."
            )

    def accepts(
        self,
        measurement: ResourceMeasurement,
    ) -> bool:
        if not isinstance(measurement, ResourceMeasurement):
            raise TypeError(
                "measurement must be a ResourceMeasurement."
            )

        return (
            measurement.operation == self.operation
            and measurement.elapsed_seconds <= self.maximum_seconds
            and measurement.memory_growth_bytes
            <= self.maximum_memory_growth_bytes
        )


def current_process_memory_bytes() -> int:
    """
    Return the current process working-set size in bytes.

    Windows uses GetProcessMemoryInfo when available. A portable
    fallback returns zero when the platform API is unavailable.
    """
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            psapi = ctypes.WinDLL("psapi")
            kernel32 = ctypes.WinDLL("kernel32")

            process = kernel32.GetCurrentProcess()

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)

            success = psapi.GetProcessMemoryInfo(
                process,
                ctypes.byref(counters),
                counters.cb,
            )

            if success:
                return int(counters.WorkingSetSize)

        except (AttributeError, OSError, TypeError, ValueError):
            pass

    return 0


def measure_resource_operation(
    operation: str,
    callback: Callable[[], T],
) -> tuple[T, ResourceMeasurement]:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not callable(callback):
        raise TypeError("callback must be callable.")

    memory_before = current_process_memory_bytes()
    start = time.perf_counter()

    result = callback()

    elapsed = time.perf_counter() - start
    memory_after = current_process_memory_bytes()

    return result, ResourceMeasurement(
        operation=operation,
        elapsed_seconds=elapsed,
        memory_before_bytes=memory_before,
        memory_after_bytes=memory_after,
    )


SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET = ResourcePerformanceBudget(
    operation="system_wide_intelligence",
    maximum_seconds=5.0,
    maximum_memory_growth_bytes=256 * 1024 * 1024,
)


def resource_usage_is_acceptable(
    measurement: ResourceMeasurement,
) -> bool:
    return SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET.accepts(
        measurement
    )
