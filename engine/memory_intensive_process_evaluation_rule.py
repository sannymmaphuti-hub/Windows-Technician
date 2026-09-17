from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class MemoryIntensiveProcessEvaluationRule(
    RootCauseEvaluationRule
):

    def matches(self, candidate, findings):

        if candidate.cause_type != "MEMORY_INTENSIVE_PROCESS":
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
                "MEMORY_INTENSIVE_PROCESS",
            }
        ]

        has_process_evidence = any(
            finding.finding_type == "MEMORY_INTENSIVE_PROCESS"
            for finding in findings
        )

        if has_process_evidence:

            return RootCauseEvaluation(
                candidate=candidate,
                supporting_evidence=supporting_evidence,
                assessment="SUPPORTED",
                explanation=(
                    "Memory pressure together with evidence of "
                    "a memory-intensive process supports this "
                    "possible cause, although further evidence "
                    "is required to establish whether the "
                    "process is the primary underlying cause."
                ),
            )

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="INSUFFICIENT",
            explanation=(
                "Memory pressure supports the possibility of "
                "a memory-intensive process, but the current "
                "evidence is insufficient to identify a specific "
                "process as the cause."
            ),
        )