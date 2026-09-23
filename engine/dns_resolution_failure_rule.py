from engine.finding import Finding
from engine.finding_rule import FindingRule


class DNSResolutionFailureRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "DNS_RESOLUTION_FAILED"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="DNS_RESOLUTION_FAILURE",
            category="NETWORK",
            severity="MEDIUM",
            description="DNS resolution is failing.",
            supporting_signals=[signal],
        )
