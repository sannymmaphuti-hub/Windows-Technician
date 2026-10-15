"""Workload sizing and admission policies for Windows Technician."""

from dataclasses import asdict, dataclass
from typing import Any

from engine.performance_scale_boundary import PerformanceScaleBoundary


@dataclass(frozen=True, slots=True)
class WorkloadEstimate:
    """Estimated resource demand for a proposed workload."""

    resource: str
    workload_size: int
    units_per_item: int
    estimated_demand: int

    def projection(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WorkloadAdmissionDecision:
    """Decision describing whether estimated demand fits available capacity."""

    status: str
    resource: str
    workload_size: int
    estimated_demand: int
    available_capacity: int
    reason: str

    @property
    def admitted(self) -> bool:
        return self.status == "ADMITTED"

    def projection(self) -> dict[str, Any]:
        return asdict(self)


class WorkloadSizingPolicy:
    """Estimates demand and evaluates capacity without executing workloads."""

    SCHEMA_VERSION = "1.0"

    _RESOURCE_UNITS = {
        "concurrent_diagnostics": "diagnostic",
        "managed_machines": "machine",
        "retained_events": "event",
        "projection_items": "projection_item",
    }

    def __init__(
        self,
        capacity_boundary: PerformanceScaleBoundary | None = None,
    ) -> None:
        self._capacity_boundary = (
            capacity_boundary or PerformanceScaleBoundary()
        )

    def estimate(
        self,
        *,
        resource: str,
        workload_size: int,
        units_per_item: int = 1,
    ) -> WorkloadEstimate:
        """Calculate resource demand using explicit integer units."""

        self._validate_resource(resource)
        self._validate_non_negative_integer("workload_size", workload_size)
        self._validate_positive_integer("units_per_item", units_per_item)

        demand = workload_size * units_per_item

        return WorkloadEstimate(
            resource=resource,
            workload_size=workload_size,
            units_per_item=units_per_item,
            estimated_demand=demand,
        )

    def evaluate(
        self,
        *,
        resource: str,
        workload_size: int,
        current: int = 0,
        units_per_item: int = 1,
    ) -> WorkloadAdmissionDecision:
        """Estimate demand and decide whether capacity can accommodate it."""

        estimate = self.estimate(
            resource=resource,
            workload_size=workload_size,
            units_per_item=units_per_item,
        )

        capacity = self._capacity_boundary.evaluate_capacity(
            resource=resource,
            requested=estimate.estimated_demand,
            current=current,
        )

        return WorkloadAdmissionDecision(
            status="ADMITTED" if capacity.admitted else "REJECTED",
            resource=resource,
            workload_size=workload_size,
            estimated_demand=estimate.estimated_demand,
            available_capacity=capacity.available,
            reason=capacity.reason,
        )

    def projection(self) -> dict[str, Any]:
        """Expose supported resource units and capacity policy."""

        return {
            "schema_version": self.SCHEMA_VERSION,
            "resource_units": dict(self._RESOURCE_UNITS),
            "capacity": self._capacity_boundary.projection(),
            "execution_performed": False,
        }

    @classmethod
    def _validate_resource(cls, resource: str) -> None:
        if not isinstance(resource, str):
            raise TypeError("resource must be a string")
        if resource not in cls._RESOURCE_UNITS:
            raise ValueError(f"Unsupported resource: {resource}")

    @staticmethod
    def _validate_non_negative_integer(name: str, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} cannot be negative")

    @classmethod
    def _validate_positive_integer(cls, name: str, value: int) -> None:
        cls._validate_non_negative_integer(name, value)
        if value < 1:
            raise ValueError(f"{name} must be at least 1")
