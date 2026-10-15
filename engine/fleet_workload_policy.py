"""Fleet-scale workload admission policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.workload_sizing_policy import WorkloadSizingPolicy


@dataclass(frozen=True, slots=True)
class FleetWorkloadDecision:
    fleet_size: int
    units_per_machine: int
    estimated_demand: int
    admitted: bool
    status: str
    reason: str

    def projection(self) -> dict[str, Any]:
        return {
            "fleet_size": self.fleet_size,
            "units_per_machine": self.units_per_machine,
            "estimated_demand": self.estimated_demand,
            "admitted": self.admitted,
            "status": self.status,
            "reason": self.reason,
            "execution_performed": False,
        }


class FleetWorkloadPolicy:
    """Evaluate fleet workload capacity without executing machine operations."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        workload_sizing_policy: WorkloadSizingPolicy | None = None,
    ) -> None:
        self._sizing = workload_sizing_policy or WorkloadSizingPolicy()

    def evaluate(
        self,
        *,
        fleet_size: int,
        units_per_machine: int = 1,
        current: int = 0,
    ) -> FleetWorkloadDecision:
        for name, value in (
            ("fleet_size", fleet_size),
            ("units_per_machine", units_per_machine),
            ("current", current),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

        if units_per_machine < 1:
            raise ValueError("units_per_machine must be positive")

        estimate = self._sizing.estimate(
            resource="concurrent_diagnostics",
            workload_size=fleet_size,
            units_per_item=units_per_machine,
        )
        admission = self._sizing.evaluate(
            resource="concurrent_diagnostics",
            workload_size=fleet_size,
            current=current,
            units_per_item=units_per_machine,
        )

        return FleetWorkloadDecision(
            fleet_size=fleet_size,
            units_per_machine=units_per_machine,
            estimated_demand=estimate.estimated_demand,
            admitted=admission.admitted,
            status=admission.status,
            reason=admission.reason,
        )

    def projection(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policy": "fleet_workload_admission",
            "execution_performed": False,
        }
