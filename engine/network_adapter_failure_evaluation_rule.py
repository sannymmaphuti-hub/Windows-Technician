from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class NetworkAdapterFailureEvaluationRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        if candidate.cause_type != "NETWORK_ADAPTER_FAILURE":
            return False

        return any(
            finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
            for finding in findings
        )

    def create_evaluation(self, candidate, findings):
        supporting_evidence = [
            finding
            for finding in findings
            if finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
        ]

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="STRONGLY_SUPPORTED",
            explanation=(
                "The network adapter is explicitly reported as "
                "disconnected, strongly supporting a network "
                "adapter problem."
            ),
        )
