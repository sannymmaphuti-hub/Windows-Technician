from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


class NetworkAdapterDiagnosticActionRule(DiagnosticActionSelectionRule):
    def matches(self, decision_type):
        return decision_type == "CHECK_NETWORK_ADAPTER"

    def create_action(self, decision_type):
        if not self.matches(decision_type):
            raise ValueError(
                f"Unsupported diagnostic decision: {decision_type}."
            )

        return DiagnosticAction(
            action_type="COLLECT_NETWORK_ADAPTER_STATE",
            category="NETWORK",
            description="Collect the current network adapter state.",
        )
