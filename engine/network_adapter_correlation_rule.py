from engine.correlation import Correlation
from engine.correlation_rule import CorrelationRule


class NetworkAdapterCorrelationRule(CorrelationRule):

    def matches(self, findings):
        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return "NETWORK_ADAPTER_DISCONNECTED" in finding_types

    def create_correlation(self, findings):
        return Correlation(
            correlation_type="NETWORK_ADAPTER_FAILURE",
            findings=findings,
            strength="HIGH",
            explanation=(
                "A disconnected network adapter is present and may "
                "be related to the loss of network connectivity."
            ),
        )
