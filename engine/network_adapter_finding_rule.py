from engine.finding import Finding
from engine.finding_rule import FindingRule


class NetworkAdapterFindingRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "NETWORK_ADAPTER_DISCONNECTED"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="NETWORK_ADAPTER_DISCONNECTED",
            category="NETWORK",
            severity="HIGH",
            description="The network adapter is disconnected.",
            supporting_signals=[signal],
        )