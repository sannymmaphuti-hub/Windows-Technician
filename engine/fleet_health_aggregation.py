from copy import deepcopy

from engine.fleet import Fleet


class FleetHealthAggregation:
    """
    Read-only fleet health aggregation.

    Aggregates the canonical health state of Fleet members.
    It does not diagnose machines, infer root causes, authorize
    remediation, execute actions, or verify remediation.
    """

    _KNOWN_STATES = {
        "HEALTHY",
        "WARNING",
        "UNKNOWN",
    }

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetHealthAggregation requires a Fleet."
            )

        self.fleet = fleet

    @property
    def machine_count(self):
        return self.fleet.machine_count

    def counts(self):
        counts = {
            "HEALTHY": 0,
            "WARNING": 0,
            "UNKNOWN": 0,
        }

        for machine in self.fleet.machines:
            state = machine.health_state

            if state not in self._KNOWN_STATES:
                state = "UNKNOWN"

            counts[state] += 1

        return counts

    def healthy_count(self):
        return self.counts()["HEALTHY"]

    def warning_count(self):
        return self.counts()["WARNING"]

    def unknown_count(self):
        return self.counts()["UNKNOWN"]

    def percentages(self):
        total = self.machine_count

        if total == 0:
            return {
                "HEALTHY": 0.0,
                "WARNING": 0.0,
                "UNKNOWN": 0.0,
            }

        counts = self.counts()

        return {
            state: (count / total) * 100
            for state, count in counts.items()
        }

    def overall_state(self):
        counts = self.counts()

        if self.machine_count == 0:
            return "UNKNOWN"

        if counts["WARNING"] > 0:
            return "WARNING"

        if counts["UNKNOWN"] > 0:
            return "UNKNOWN"

        return "HEALTHY"

    def machine_breakdown(self):
        return deepcopy(
            [
                {
                    "machine_id": machine.machine_id,
                    "hostname": machine.hostname,
                    "health_state": (
                        machine.health_state
                        if machine.health_state in self._KNOWN_STATES
                        else "UNKNOWN"
                    ),
                }
                for machine in self.fleet.machines
            ]
        )

    def projection(self):
        return {
            "machine_count": self.machine_count,
            "overall_state": self.overall_state(),
            "counts": self.counts(),
            "percentages": self.percentages(),
            "machines": self.machine_breakdown(),
        }
