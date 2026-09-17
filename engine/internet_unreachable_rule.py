from engine.signal import Signal
from engine.signal_rule import SignalRule


class InternetUnreachableRule(SignalRule):

    def matches(self, observation):
        return (
            observation.source == "network"
            and observation.subject == "network_internet"
            and observation.attribute == "reachable"
            and observation.value is False
        )

    def create_signal(self, observation):
        return Signal(
            signal_type="INTERNET_UNREACHABLE",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
        )