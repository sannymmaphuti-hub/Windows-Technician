from engine.finding import Finding
from engine.finding_rule import FindingRule


class LocalNetworkUnreachableRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "DEFAULT_GATEWAY_UNREACHABLE"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="LOCAL_NETWORK_UNREACHABLE",
            category="NETWORK",
            severity="HIGH",
            description="The local network gateway is unreachable.",
            supporting_signals=[signal],
        )
