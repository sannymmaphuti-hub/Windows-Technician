from engine.signal import Signal
from engine.signal_rule import SignalRule


class DNSResolutionFailedRule(SignalRule):

    def matches(self, observation):
        return (
            observation.source == "network"
            and observation.subject == "network_dns"
            and observation.attribute == "working"
            and observation.value is False
        )

    def create_signal(self, observation):
        return Signal(
            signal_type="DNS_RESOLUTION_FAILED",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
        )