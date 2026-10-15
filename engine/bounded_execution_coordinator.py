"""Thread-safe bounded workload reservations for Windows Technician."""

from dataclasses import asdict, dataclass
from threading import RLock
from typing import Any
from uuid import uuid4

from engine.bounded_history_store import BoundedHistoryStore
from engine.performance_scale_boundary import (
    PerformanceLimits,
    PerformanceScaleBoundary,
)


@dataclass(frozen=True, slots=True)
class ReservationDecision:
    """Result of attempting to reserve capacity for a workload."""

    admitted: bool
    reservation_id: str | None
    resource: str
    units: int
    available_capacity: int
    reason: str

    def projection(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReservationRecord:
    """Immutable snapshot of a reservation's lifecycle."""

    reservation_id: str
    resource: str
    units: int
    status: str

    def projection(self) -> dict[str, Any]:
        return asdict(self)


class BoundedExecutionCoordinator:
    """Atomically reserves bounded capacity without executing workloads.

    A reservation represents admitted capacity, not an executed operation.
    Callers remain responsible for invoking and supervising actual work.
    """

    SCHEMA_VERSION = "1.0"

    _RESOURCE_LIMITS = {
        "concurrent_diagnostics": "max_concurrent_diagnostics",
        "managed_machines": "max_managed_machines",
        "retained_events": "max_events_retained",
        "projection_items": "max_projection_items",
    }

    def __init__(
        self,
        limits: PerformanceLimits | None = None,
        *,
        history_capacity: int | None = None,
    ) -> None:
        self._limits = limits or PerformanceLimits()
        self._capacity = PerformanceScaleBoundary(self._limits)
        self._lock = RLock()
        self._active: dict[str, ReservationRecord] = {}

        if history_capacity is None:
            history_capacity = self._limits.max_events_retained

        self._history = BoundedHistoryStore(capacity=history_capacity)

    def reserve(
        self,
        *,
        resource: str = "concurrent_diagnostics",
        units: int = 1,
    ) -> ReservationDecision:
        """Atomically admit a reservation if sufficient capacity remains."""

        self._validate_resource(resource)
        self._validate_units(units)

        with self._lock:
            current = sum(
                record.units
                for record in self._active.values()
                if record.resource == resource
            )

            capacity = self._capacity.evaluate_capacity(
                resource=resource,
                requested=units,
                current=current,
            )

            if not capacity.admitted:
                return ReservationDecision(
                    admitted=False,
                    reservation_id=None,
                    resource=resource,
                    units=units,
                    available_capacity=capacity.available,
                    reason=capacity.reason,
                )

            reservation_id = uuid4().hex
            record = ReservationRecord(
                reservation_id=reservation_id,
                resource=resource,
                units=units,
                status="ACTIVE",
            )

            self._active[reservation_id] = record
            self._history.append(record)

            return ReservationDecision(
                admitted=True,
                reservation_id=reservation_id,
                resource=resource,
                units=units,
                available_capacity=capacity.available - units,
                reason="RESERVED",
            )

    def complete(self, reservation_id: str) -> bool:
        """Mark an active reservation completed and release its capacity.

        Returns False when the identifier is unknown or is no longer active.
        Repeated calls therefore cannot release capacity more than once.
        """

        return self._finish(reservation_id, "COMPLETED")

    def release(self, reservation_id: str) -> bool:
        """Release an active reservation without claiming work completed."""

        return self._finish(reservation_id, "RELEASED")

    def _finish(self, reservation_id: str, status: str) -> bool:
        if not isinstance(reservation_id, str):
            raise TypeError("reservation_id must be a string")

        with self._lock:
            record = self._active.pop(reservation_id, None)

            if record is None:
                return False

            self._history.append(
                ReservationRecord(
                    reservation_id=record.reservation_id,
                    resource=record.resource,
                    units=record.units,
                    status=status,
                )
            )
            return True

    def projection(self) -> dict[str, Any]:
        """Return a detached, consistent snapshot of coordinator state."""

        with self._lock:
            active_records = list(self._active.values())
            history_snapshot = self._history.projection()
            history_records = history_snapshot["records"]

            active_units = {
                resource: sum(
                    record.units
                    for record in active_records
                    if record.resource == resource
                )
                for resource in self._RESOURCE_LIMITS
            }

            resource_limits = {
                resource: getattr(self._limits, limit_name)
                for resource, limit_name in self._RESOURCE_LIMITS.items()
            }

            return {
                "schema_version": self.SCHEMA_VERSION,
                "limits": asdict(self._limits),
                "resource_limits": resource_limits,
                "active_reservation_count": len(active_records),
                "active_units_by_resource": active_units,
                "available_capacity_by_resource": {
                    resource: max(
                        0,
                        resource_limits[resource] - active_units[resource],
                    )
                    for resource in self._RESOURCE_LIMITS
                },
                "active_reservations": [
                    record.projection() for record in active_records
                ],
                "history": [
                    record.projection() for record in history_records
                ],
                "history_capacity": history_snapshot["capacity"],
                "history_evicted_count": history_snapshot["evicted_count"],
                "execution_performed": False,
            }

    @classmethod
    def _validate_resource(cls, resource: str) -> None:
        if not isinstance(resource, str):
            raise TypeError("resource must be a string")

        if resource not in cls._RESOURCE_LIMITS:
            raise ValueError(f"Unsupported resource: {resource}")

    @staticmethod
    def _validate_units(units: int) -> None:
        if isinstance(units, bool) or not isinstance(units, int):
            raise TypeError("units must be an integer")

        if units < 1:
            raise ValueError("units must be at least 1")
