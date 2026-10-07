from engine.fleet import Fleet
from engine.fleet_investigation_target import FleetInvestigationTarget
from engine.fleet_problem_pattern import FleetProblemPattern


class FleetInvestigationTargeting:

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError("fleet must be a Fleet")

        self.fleet = fleet

    def select(self, pattern):
        if not isinstance(pattern, FleetProblemPattern):
            raise ValueError(
                "pattern must be a FleetProblemPattern"
            )

        targets = []

        for machine_id in pattern.machine_ids:
            if not self.fleet.contains_machine(machine_id):
                continue

            targets.append(
                FleetInvestigationTarget(
                    machine_id=machine_id,
                    problem_type=pattern.problem_type,
                    domain=pattern.domain,
                    reason=(
                        "Machine is affected by the fleet "
                        "problem pattern and requires "
                        "individual investigation."
                    ),
                )
            )

        return targets
