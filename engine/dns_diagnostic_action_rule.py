from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


class DNSDiagnosticActionRule(DiagnosticActionSelectionRule):
    def matches(self, decision_type):
        return decision_type == "CHECK_DNS_RESOLUTION"

    def create_action(self, decision_type):
        if not self.matches(decision_type):
            raise ValueError(
                f"Unsupported diagnostic decision: {decision_type}."
            )

        return DiagnosticAction(
            action_type="TEST_DNS_RESOLUTION",
            category="NETWORK",
            description="Check whether DNS resolution is working.",
        )
