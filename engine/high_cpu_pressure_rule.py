from engine.finding import Finding
from engine.finding_rule import FindingRule


class HighCpuPressureRule(FindingRule):

    def matches(self, signal):
        return (
            signal.signal_type == "HIGH_CPU_USAGE"
            and signal.source == "cpu"
            and signal.subject == "system_cpu"
            and signal.attribute == "usage_percent"
        )

    def create_finding(self, signal):
        return Finding(
            finding_type="CPU_PRESSURE",
            category="CPU",
            severity=self._determine_severity(signal),
            description="System CPU pressure is high.",
            supporting_signals=[signal],
        )

    @staticmethod
    def _determine_severity(signal):
        if signal.value >= 99:
            return "HIGH"

        if signal.value >= 95:
            return "MEDIUM"

        return "LOW"
