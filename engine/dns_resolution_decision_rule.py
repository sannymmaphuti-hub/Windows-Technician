from engine.diagnostic_decision import DiagnosticDecision
from engine.diagnostic_decision_rule import DiagnosticDecisionRule


class DNSResolutionDecisionRule(DiagnosticDecisionRule):
    def matches(self, evidence):
        active_adapter = evidence.get("active_adapter")

        if active_adapter is None:
            return False

        if not isinstance(active_adapter, dict):
            raise ValueError("active_adapter must be a dictionary.")

        if active_adapter.get("is_up") is not True:
            return False

        if evidence.get("gateway_reachable") is not True:
            return False

        return "dns_working" not in evidence

    def create_decision(self, evidence):
        return DiagnosticDecision(
            decision_type="CHECK_DNS_RESOLUTION",
            category="NETWORK",
            reason="DNS resolution status is unknown.",
            priority="HIGH",
        )
