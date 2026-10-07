class FleetProblemPattern:
    """Represents the fleet-wide distribution of a known problem."""

    PATTERN_TYPES = {
        "ISOLATED",
        "REPEATED",
        "WIDESPREAD",
    }

    def __init__(
        self,
        problem_type,
        domain,
        machine_ids,
        fleet_machine_count,
    ):
        if not problem_type:
            raise ValueError("problem_type is required")

        if not domain:
            raise ValueError("domain is required")

        if fleet_machine_count < 0:
            raise ValueError("fleet_machine_count cannot be negative")

        unique_machine_ids = list(dict.fromkeys(machine_ids))

        if any(machine_id is None for machine_id in unique_machine_ids):
            raise ValueError("machine_ids cannot contain None")

        if len(unique_machine_ids) > fleet_machine_count:
            raise ValueError(
                "affected machines cannot exceed fleet machine count"
            )

        self.problem_type = problem_type
        self.domain = domain
        self.machine_ids = unique_machine_ids
        self.fleet_machine_count = fleet_machine_count

    @property
    def affected_machine_count(self):
        return len(self.machine_ids)

    @property
    def affected_machine_ratio(self):
        if self.fleet_machine_count == 0:
            return 0.0

        return self.affected_machine_count / self.fleet_machine_count

    @property
    def pattern_type(self):
        if self.affected_machine_count <= 1:
            return "ISOLATED"

        if self.affected_machine_ratio >= 0.5:
            return "WIDESPREAD"

        return "REPEATED"

    @property
    def scope(self):
        return self.pattern_type

    def to_evidence(self):
        return {
            "problem_type": self.problem_type,
            "domain": self.domain,
            "machine_ids": list(self.machine_ids),
            "affected_machine_count": self.affected_machine_count,
            "fleet_machine_count": self.fleet_machine_count,
            "affected_machine_ratio": self.affected_machine_ratio,
            "pattern_type": self.pattern_type,
            "scope": self.scope,
        }
