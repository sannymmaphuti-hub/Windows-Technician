from engine.finding import Finding
from engine.finding_rule import FindingRule


class HighMemoryPressureRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "HIGH_MEMORY_USAGE"
            and signal.source == "memory"
            and signal.subject == "system_memory"
            and signal.attribute == "usage_percent"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="MEMORY_PRESSURE",
            category="MEMORY",
            severity=self._determine_severity(signal),
            description="System memory pressure is high.",
            supporting_signals=[signal],
        )

    @staticmethod
    def _determine_severity(signal):
        if signal.value >= 95:
            return "HIGH"

        if signal.value >= 90:
            return "MEDIUM"

        return "LOW"
