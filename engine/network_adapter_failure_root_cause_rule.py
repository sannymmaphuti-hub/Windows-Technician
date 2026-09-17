from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class NetworkAdapterFailureRootCauseRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="NETWORK_ADAPTER_FAILURE",
            category="NETWORK",
            explanation=(
                "The network adapter is disconnected, which may "
                "prevent the computer from communicating with the network."
            ),
        )