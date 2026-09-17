from engine.signal_rule import SignalRule
from engine.signal import Signal


class HighCpuUsageRule(SignalRule):

    THRESHOLD = 90

    def matches(self, observation):
        return (
            observation.source == "cpu"
            and observation.subject == "system_cpu"
            and observation.attribute == "usage_percent"
            and observation.value >= self.THRESHOLD
        )

    def create_signal(self, observation):
        return Signal(
            signal_type="HIGH_CPU_USAGE",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
            strength=self._determine_strength(observation.value),
        )

    @staticmethod
    def _determine_strength(value):
        if value >= 99:
            return "HIGH"

        if value >= 95:
            return "MEDIUM"

        return "LOW"