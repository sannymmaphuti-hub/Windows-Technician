from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class MemoryLeakEvaluationRule(
    RootCauseEvaluationRule
):

    def matches(self, candidate, findings):

        if candidate.cause_type != "MEMORY_LEAK":
            return False

        return any(
            finding.finding_type == "MEMORY_PRESSURE"
            for finding in findings
        )

    def create_evaluation(self, candidate, findings):

        supporting_evidence = [
            finding
            for finding in findings
            if finding.finding_type
            in {
                "MEMORY_PRESSURE",
                "MEMORY_GROWTH_OVER_TIME",
            }
        ]

        has_memory_growth = any(
            finding.finding_type
            == "MEMORY_GROWTH_OVER_TIME"
            for finding in findings
        )

        if has_memory_growth:

            return RootCauseEvaluation(
                candidate=candidate,
                supporting_evidence=supporting_evidence,
                assessment="SUPPORTED",
                explanation=(
                    "Memory pressure together with evidence "
                    "of sustained memory growth supports the "
                    "possibility of a memory leak, although "
                    "further evidence is required to establish "
                    "whether a memory leak is the primary "
                    "underlying cause."
                ),
            )

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="INSUFFICIENT",
            explanation=(
                "Memory pressure alone is insufficient to "
                "support a memory leak. Evidence of sustained "
                "memory growth over time is required."
            ),
        )