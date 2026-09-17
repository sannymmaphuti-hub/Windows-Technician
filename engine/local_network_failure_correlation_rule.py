from engine.correlation import Correlation
from engine.correlation_rule import CorrelationRule


class LocalNetworkFailureCorrelationRule(CorrelationRule):

    def matches(self, findings):
        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return (
            "LOCAL_NETWORK_UNREACHABLE" in finding_types
            and "INTERNET_CONNECTIVITY_FAILURE" in finding_types
        )

    def create_correlation(self, findings):
        return Correlation(
            correlation_type="LOCAL_NETWORK_FAILURE",
            findings=findings,
            strength="HIGH",
            explanation=(
                "The local network gateway is unreachable while "
                "Internet connectivity is unavailable, indicating "
                "a possible local network connectivity problem."
            ),
        )