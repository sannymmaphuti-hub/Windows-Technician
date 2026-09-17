from engine.signal import Signal
from engine.signal_rule import SignalRule


class NetworkAdapterDisconnectedRule(SignalRule):

    def matches(self, observation):
        return (
            observation.source == "network"
            and observation.subject == "network_adapter"
            and observation.attribute == "is_up"
            and observation.value is False
        )

    def create_signal(self, observation):
        return Signal(
            signal_type="NETWORK_ADAPTER_DISCONNECTED",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
        )