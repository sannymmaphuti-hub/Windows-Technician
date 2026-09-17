from engine.diagnostic_decision import DiagnosticDecision


class DiagnosticDecisionEngine:
    def decide(self, evidence):
        if not isinstance(evidence, dict):
            raise ValueError("evidence must be a dictionary.")

        if not evidence:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_NETWORK_ADAPTER",
                    category="NETWORK",
                    reason="Network adapter state is unknown.",
                    priority="HIGH",
                )
            ]

        active_adapter = evidence.get("active_adapter")

        if active_adapter is None:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_NETWORK_ADAPTER",
                    category="NETWORK",
                    reason="Network adapter state is unknown.",
                    priority="HIGH",
                )
            ]

        if not isinstance(active_adapter, dict):
            raise ValueError("active_adapter must be a dictionary.")

        if "is_up" not in active_adapter:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_NETWORK_ADAPTER",
                    category="NETWORK",
                    reason="Network adapter state is unknown.",
                    priority="HIGH",
                )
            ]

        if active_adapter.get("is_up") is not True:
            return []

        if "gateway_reachable" not in evidence:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_GATEWAY_REACHABILITY",
                    category="NETWORK",
                    reason="Gateway reachability is unknown.",
                    priority="HIGH",
                )
            ]

        if evidence.get("gateway_reachable") is not True:
            return []

        if "dns_working" not in evidence:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_DNS_RESOLUTION",
                    category="NETWORK",
                    reason="DNS resolution status is unknown.",
                    priority="HIGH",
                )
            ]

        if evidence.get("dns_working") is not True:
            return []

        if "internet_reachable" not in evidence:
            return [
                DiagnosticDecision(
                    decision_type="CHECK_INTERNET_CONNECTIVITY",
                    category="NETWORK",
                    reason="Internet connectivity status is unknown.",
                    priority="HIGH",
                )
            ]

        return []