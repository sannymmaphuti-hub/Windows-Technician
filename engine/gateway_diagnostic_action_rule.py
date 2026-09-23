from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


class GatewayDiagnosticActionRule(DiagnosticActionSelectionRule):
    def matches(self, decision_type):
        return decision_type == "CHECK_GATEWAY_REACHABILITY"

    def create_action(self, decision_type):
        if not self.matches(decision_type):
            raise ValueError(
                f"Unsupported diagnostic decision: {decision_type}."
            )

        return DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Check whether the default gateway is reachable.",
        )
