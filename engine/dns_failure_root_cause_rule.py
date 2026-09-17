from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class DNSFailureRootCauseRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "DNS_RESOLUTION_FAILURE"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="DNS_FAILURE",
            category="NETWORK",
            explanation=(
                "DNS resolution is failing, which may prevent "
                "the computer from locating Internet services."
            ),
        )