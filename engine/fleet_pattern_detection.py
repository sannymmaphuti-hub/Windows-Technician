from engine.fleet_problem import FleetProblem
from engine.fleet_problem_pattern import FleetProblemPattern


class FleetPatternDetection:
    """Detects distribution patterns from existing FleetProblem objects."""

    def __init__(self, fleet):
        if fleet is None:
            raise ValueError("fleet is required")

        self.fleet = fleet

    def detect(self, problems):
        if not isinstance(problems, list):
            raise ValueError("problems must be a list")

        patterns = []

        for problem in problems:
            if not isinstance(problem, FleetProblem):
                raise ValueError(
                    "all problems must be FleetProblem instances"
                )

            machine_ids = [
                machine_id
                for machine_id in problem.machine_ids
                if self.fleet.contains_machine(machine_id)
            ]

            if not machine_ids:
                continue

            patterns.append(
                FleetProblemPattern(
                    problem_type=problem.problem_type,
                    domain=problem.domain,
                    machine_ids=machine_ids,
                    fleet_machine_count=self.fleet.machine_count,
                )
            )

        return patterns
