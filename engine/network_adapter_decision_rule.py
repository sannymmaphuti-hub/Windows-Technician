from engine.diagnostic_decision import DiagnosticDecision
from engine.diagnostic_decision_rule import DiagnosticDecisionRule


class NetworkAdapterDecisionRule(DiagnosticDecisionRule):
    def matches(self, evidence):
        active_adapter = evidence.get("active_adapter")

        if active_adapter is None:
            return True

        if not isinstance(active_adapter, dict):
            raise ValueError("active_adapter must be a dictionary.")

        return "is_up" not in active_adapter

    def create_decision(self, evidence):
        return DiagnosticDecision(
            decision_type="CHECK_NETWORK_ADAPTER",
            category="NETWORK",
            reason="Network adapter state is unknown.",
            priority="HIGH",
        )