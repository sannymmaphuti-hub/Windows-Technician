from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule


class DNSFailureEvaluationRule(RootCauseEvaluationRule):

    def matches(self, candidate, findings):
        if candidate.cause_type != "DNS_FAILURE":
            return False

        return any(
            finding.finding_type == "DNS_RESOLUTION_FAILURE"
            for finding in findings
        )

    def create_evaluation(self, candidate, findings):
        supporting_evidence = [
            finding
            for finding in findings
            if finding.finding_type == "DNS_RESOLUTION_FAILURE"
        ]

        return RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=supporting_evidence,
            assessment="SUPPORTED",
            explanation=(
                "DNS resolution failure is directly supported by "
                "the DNS failure finding."
            ),
        )