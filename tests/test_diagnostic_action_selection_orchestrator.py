from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selection_orchestrator import (
    DiagnosticActionSelectionOrchestrator,
)


class StubRule:
    def __init__(self, matches_result, action_type="TEST_ACTION"):
        self.matches_result = matches_result
        self.action_type = action_type

    def matches(self, decision_type):
        return self.matches_result

    def create_action(self, decision_type):
        return DiagnosticAction(
            action_type=self.action_type,
            category="NETWORK",
            description="Test diagnostic action.",
        )


def test_orchestrator_returns_action_from_matching_rule():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    orchestrator.register_rule(
        StubRule(True, "TEST_GATEWAY_ACTION")
    )

    action = orchestrator.select("CHECK_GATEWAY_REACHABILITY")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "TEST_GATEWAY_ACTION"


def test_orchestrator_returns_no_action_when_no_rule_matches():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    orchestrator.register_rule(StubRule(False))

    assert orchestrator.select("CHECK_GATEWAY_REACHABILITY") is None


def test_orchestrator_uses_first_matching_rule():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    orchestrator.register_rule(
        StubRule(True, "FIRST_ACTION")
    )
    orchestrator.register_rule(
        StubRule(True, "SECOND_ACTION")
    )

    action = orchestrator.select("CHECK_GATEWAY_REACHABILITY")

    assert action.action_type == "FIRST_ACTION"


def test_orchestrator_rejects_rule_without_matches():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    class InvalidRule:
        def create_action(self, decision_type):
            return None

    try:
        orchestrator.register_rule(InvalidRule())
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_orchestrator_rejects_rule_without_create_action():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    class InvalidRule:
        def matches(self, decision_type):
            return True

    try:
        orchestrator.register_rule(InvalidRule())
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_orchestrator_rejects_non_string_decision():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    try:
        orchestrator.select(123)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_orchestrator_rejects_empty_decision():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    try:
        orchestrator.select("")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")