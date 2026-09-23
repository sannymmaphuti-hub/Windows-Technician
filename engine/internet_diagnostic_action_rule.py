from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selection_rule import (
    DiagnosticActionSelectionRule,
)


class InternetDiagnosticActionRule(DiagnosticActionSelectionRule):
    def matches(self, decision_type):
        return decision_type == "CHECK_INTERNET_CONNECTIVITY"

    def create_action(self, decision_type):
        if not self.matches(decision_type):
            raise ValueError(
                f"Unsupported diagnostic decision: {decision_type}."
            )

        return DiagnosticAction(
            action_type="TEST_INTERNET_CONNECTIVITY",
            category="NETWORK",
            description="Check whether Internet connectivity is available.",
        )
