from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class LocalNetworkFailureRootCauseRule(RootCauseRule):

    def matches(self, findings):
        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return (
            "LOCAL_NETWORK_UNREACHABLE" in finding_types
            and "INTERNET_CONNECTIVITY_FAILURE" in finding_types
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="LOCAL_NETWORK_FAILURE",
            category="NETWORK",
            explanation=(
                "The local network gateway is unreachable while "
                "Internet connectivity is unavailable, indicating "
                "a possible local network connectivity problem."
            ),
        )
