from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class LocalNetworkFailureEvaluationRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        if candidate.cause_type != "LOCAL_NETWORK_FAILURE":
            return False

        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return (
            "LOCAL_NETWORK_UNREACHABLE" in finding_types
            and "INTERNET_CONNECTIVITY_FAILURE" in finding_types
        )

    def create_evaluation(self, candidate, findings):
        supporting_evidence = [
            finding
            for finding in findings
            if finding.finding_type in {
                "LOCAL_NETWORK_UNREACHABLE",
                "INTERNET_CONNECTIVITY_FAILURE",
            }
        ]

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="STRONGLY_SUPPORTED",
            explanation=(
                "The local gateway is unreachable and Internet "
                "connectivity is unavailable. Together, these "
                "findings strongly support a local network "
                "connectivity problem."
            ),
        )