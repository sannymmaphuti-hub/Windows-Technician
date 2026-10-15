from copy import deepcopy

from engine.fleet import Fleet
from engine.fleet_health_aggregation import FleetHealthAggregation


class FleetHealthIntelligence:
    """
    V1.0 fleet-level health intelligence boundary.

    Builds fleet-level operational intelligence from the canonical
    FleetHealthAggregation surface.

    This class does not:
    - diagnose individual machines
    - infer root causes
    - create DiagnosticCases
    - create remediation actions
    - authorize remediation
    - execute remediation
    - verify remediation
    - mutate Fleet state
    """

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetHealthIntelligence requires a Fleet."
            )

        self.fleet = fleet
        self.health = FleetHealthAggregation(fleet)

    @property
    def machine_count(self):
        return self.health.machine_count

    def overall_state(self):
        return self.health.overall_state()

    def counts(self):
        return deepcopy(self.health.counts())

    def percentages(self):
        return deepcopy(self.health.percentages())

    def affected_machine_count(self):
        return (
            self.health.warning_count()
            + self.health.unknown_count()
        )

    def healthy_percentage(self):
        return self.percentages()["HEALTHY"]

    def warning_percentage(self):
        return self.percentages()["WARNING"]

    def unknown_percentage(self):
        return self.percentages()["UNKNOWN"]

    def health_concentration(self):
        """
        Describe how concentrated the fleet health state is.

        Returns one of:
        - EMPTY
        - HEALTHY
        - WARNING
        - UNKNOWN
        - MIXED
        """
        if self.machine_count == 0:
            return "EMPTY"

        counts = self.counts()

        non_zero = [
            state
            for state, count in counts.items()
            if count > 0
        ]

        if len(non_zero) == 1:
            return non_zero[0]

        return "MIXED"

    def affected_machines(self):
        """
        Return machines requiring technician attention because their
        canonical fleet health state is WARNING or UNKNOWN.
        """
        return deepcopy(
            [
                machine
                for machine in self.health.machine_breakdown()
                if machine["health_state"] in {"WARNING", "UNKNOWN"}
            ]
        )

    def technician_attention_required(self):
        """
        Return whether the fleet contains any non-healthy machines.
        """
        return self.affected_machine_count() > 0

    def projection(self):
        """
        Return the canonical read-only fleet health intelligence
        projection.
        """
        return {
            "machine_count": self.machine_count,
            "overall_state": self.overall_state(),
            "counts": self.counts(),
            "percentages": self.percentages(),
            "affected_machine_count": self.affected_machine_count(),
            "healthy_percentage": self.healthy_percentage(),
            "warning_percentage": self.warning_percentage(),
            "unknown_percentage": self.unknown_percentage(),
            "health_concentration": self.health_concentration(),
            "technician_attention_required": (
                self.technician_attention_required()
            ),
            "affected_machines": self.affected_machines(),
        }
