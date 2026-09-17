from engine.correlation import Correlation
from engine.correlation_rule import CorrelationRule


class ResourceContentionRule(CorrelationRule):

    def matches(self, findings):
        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return (
            "MEMORY_PRESSURE" in finding_types
            and "CPU_PRESSURE" in finding_types
        )

    def create_correlation(self, findings):
        return Correlation(
            correlation_type="RESOURCE_CONTENTION",
            findings=findings,
            strength="MEDIUM",
            explanation=(
                "High CPU and memory pressure may be occurring "
                "together and could indicate competing resource demand."
            ),
        )