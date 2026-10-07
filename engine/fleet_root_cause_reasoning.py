from engine.fleet_root_cause_evidence import FleetRootCauseEvidence
from engine.fleet_problem_pattern import FleetProblemPattern


class FleetRootCauseReasoning:
    """Runs existing root-cause reasoning against fleet patterns."""

    def __init__(self, root_cause_reasoning):
        if root_cause_reasoning is None:
            raise ValueError(
                "root_cause_reasoning is required."
            )

        self.root_cause_reasoning = root_cause_reasoning

    def analyze(self, pattern):
        if not isinstance(pattern, FleetProblemPattern):
            raise ValueError(
                "pattern must be a FleetProblemPattern."
            )

        finding = FleetRootCauseEvidence(pattern).to_finding()

        result = self.root_cause_reasoning.analyze([finding])

        return {
            "pattern": pattern,
            "finding": finding,
            "candidates": result["candidates"],
            "evaluations": result["evaluations"],
            "confidences": result["confidences"],
            "primary_cause": result["primary_cause"],
        }
