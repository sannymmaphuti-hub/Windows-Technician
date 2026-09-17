from engine.diagnostic_action import DiagnosticAction


class DiagnosticActionSelector:
    ACTIONS = {
        "CHECK_NETWORK_ADAPTER": DiagnosticAction(
            action_type="COLLECT_NETWORK_ADAPTER_STATE",
            category="NETWORK",
            description="Collect the current network adapter state.",
        ),
        "CHECK_GATEWAY_REACHABILITY": DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Check whether the default gateway is reachable.",
        ),
        "CHECK_DNS_RESOLUTION": DiagnosticAction(
            action_type="TEST_DNS_RESOLUTION",
            category="NETWORK",
            description="Check whether DNS resolution is working.",
        ),
        "CHECK_INTERNET_CONNECTIVITY": DiagnosticAction(
            action_type="TEST_INTERNET_CONNECTIVITY",
            category="NETWORK",
            description="Check whether Internet connectivity is available.",
        ),
    }

    def select(self, decision_type):
        if not isinstance(decision_type, str) or not decision_type.strip():
            raise ValueError(
                "decision_type must be a non-empty string."
            )

        try:
            return self.ACTIONS[decision_type]
        except KeyError:
            raise ValueError(
                f"Unknown diagnostic decision: {decision_type}."
            )