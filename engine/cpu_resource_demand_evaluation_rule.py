from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class CpuResourceDemandEvaluationRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        if candidate.cause_type != "CPU_RESOURCE_DEMAND":
            return False

        return any(
            finding.finding_type == "CPU_PRESSURE"
            for finding in findings
        )

    def create_evaluation(self, candidate, findings):
        supporting_evidence = [
            finding
            for finding in findings
            if finding.finding_type == "CPU_PRESSURE"
        ]

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="INSUFFICIENT",
            explanation=(
                "CPU pressure supports the possibility of unusually "
                "high resource demand, but the current evidence is "
                "insufficient to identify the underlying source."
            ),
        )