from engine.finding import Finding
from engine.finding_rule import FindingRule


class InternetConnectivityFailureRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "INTERNET_UNREACHABLE"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="INTERNET_CONNECTIVITY_FAILURE",
            category="NETWORK",
            severity="HIGH",
            description="Internet connectivity is unavailable.",
            supporting_signals=[signal],
        )
