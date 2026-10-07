from engine.finding import Finding
from engine.fleet_problem_pattern import FleetProblemPattern


class FleetRootCauseEvidence:
    """Adapts a FleetProblemPattern into the existing Finding contract."""

    def __init__(self, pattern):
        if not isinstance(pattern, FleetProblemPattern):
            raise ValueError(
                "pattern must be a FleetProblemPattern."
            )

        self.pattern = pattern

    def to_finding(self):
        description = (
            f"{self.pattern.problem_type} affects "
            f"{self.pattern.affected_machine_count} of "
            f"{self.pattern.fleet_machine_count} fleet machines."
        )

        supporting_signals = [
            {
                "fleet_scope": self.pattern.pattern_type,
                "affected_machine_count": (
                    self.pattern.affected_machine_count
                ),
                "fleet_machine_count": (
                    self.pattern.fleet_machine_count
                ),
                "affected_machine_ratio": (
                    self.pattern.affected_machine_ratio
                ),
                "machine_ids": list(self.pattern.machine_ids),
            }
        ]

        return Finding(
            finding_type=self.pattern.problem_type,
            category=self.pattern.domain,
            severity="MEDIUM",
            description=description,
            supporting_signals=supporting_signals,
        )
