from engine.fleet_problem_pattern import FleetProblemPattern
from engine.recommendation import Recommendation


class FleetRecommendationContext:

    def __init__(
        self,
        pattern,
        finding,
        candidates,
        evaluations,
        confidences,
        primary_cause,
    ):
        if not isinstance(pattern, FleetProblemPattern):
            raise ValueError(
                "pattern must be a FleetProblemPattern."
            )

        if finding is None:
            raise ValueError("finding is required.")

        if not isinstance(candidates, list):
            raise ValueError("candidates must be a list.")

        if not isinstance(evaluations, list):
            raise ValueError("evaluations must be a list.")

        if not isinstance(confidences, list):
            raise ValueError("confidences must be a list.")

        self.pattern = pattern
        self.finding = finding
        self.candidates = list(candidates)
        self.evaluations = list(evaluations)
        self.confidences = list(confidences)
        self.primary_cause = primary_cause

    @property
    def affected_machine_count(self):
        return self.pattern.affected_machine_count

    @property
    def fleet_machine_count(self):
        return self.pattern.fleet_machine_count

    @property
    def affected_machine_ratio(self):
        return self.pattern.affected_machine_ratio

    @property
    def pattern_type(self):
        return self.pattern.pattern_type

    def to_evidence(self):
        return {
            "problem_type": self.pattern.problem_type,
            "domain": self.pattern.domain,
            "pattern_type": self.pattern_type,
            "affected_machine_count": self.affected_machine_count,
            "fleet_machine_count": self.fleet_machine_count,
            "affected_machine_ratio": self.affected_machine_ratio,
            "machine_ids": list(self.pattern.machine_ids),
            "finding_type": self.finding.finding_type,
            "candidate_count": len(self.candidates),
            "evaluation_count": len(self.evaluations),
            "confidence_count": len(self.confidences),
            "primary_cause": (
                self.primary_cause.cause_type
                if self.primary_cause is not None
                else None
            ),
        }
