from engine.high_cpu_usage_rule import HighCpuUsageRule
from engine.high_memory_usage_rule import HighMemoryUsageRule
from engine.network_adapter_disconnected_rule import (
    NetworkAdapterDisconnectedRule,
)
from engine.default_gateway_unreachable_rule import (
    DefaultGatewayUnreachableRule,
)
from engine.dns_resolution_failed_rule import (
    DNSResolutionFailedRule,
)
from engine.internet_unreachable_rule import (
    InternetUnreachableRule,
)
from engine.signal_rule import SignalRule


class ObservationToSignal:

    def __init__(self):
        self._rules = [
            HighMemoryUsageRule(),
            HighCpuUsageRule(),
            NetworkAdapterDisconnectedRule(),
            DefaultGatewayUnreachableRule(),
            DNSResolutionFailedRule(),
            InternetUnreachableRule(),
        ]

    def register_rule(self, rule):
        if not isinstance(rule, SignalRule):
            raise ValueError("rule must be a SignalRule.")

        self._rules.append(rule)

    def detect(self, observation):
        for rule in self._rules:
            if rule.matches(observation):
                return rule.create_signal(observation)

        return None
