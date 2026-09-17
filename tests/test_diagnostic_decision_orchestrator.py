from engine.diagnostic_decision import DiagnosticDecision
from engine.diagnostic_decision_orchestrator import (
    DiagnosticDecisionOrchestrator,
)


class StubRule:
    def __init__(self, matches_result, decision_type):
        self.matches_result = matches_result
        self.decision_type = decision_type

    def matches(self, evidence):
        return self.matches_result

    def create_decision(self, evidence):
        return DiagnosticDecision(
            decision_type=self.decision_type,
            category="NETWORK",
            reason="Stub decision.",
            priority="HIGH",
        )


def test_orchestrator_can_be_created():
    orchestrator = DiagnosticDecisionOrchestrator()

    assert orchestrator is not None


def test_orchestrator_can_register_a_rule():
    orchestrator = DiagnosticDecisionOrchestrator()
    rule = StubRule(True, "TEST_DECISION")

    orchestrator.register_rule(rule)

    assert len(orchestrator.rules) == 1


def test_orchestrator_returns_empty_when_no_rule_matches():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(
        StubRule(False, "TEST_DECISION")
    )

    decisions = orchestrator.decide({})

    assert decisions == []


def test_orchestrator_returns_decision_when_rule_matches():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(
        StubRule(True, "TEST_DECISION")
    )

    decisions = orchestrator.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "TEST_DECISION"


def test_orchestrator_uses_first_matching_rule():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(
        StubRule(True, "FIRST_DECISION")
    )
    orchestrator.register_rule(
        StubRule(True, "SECOND_DECISION")
    )

    decisions = orchestrator.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "FIRST_DECISION"


def test_orchestrator_does_not_return_multiple_decisions():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(
        StubRule(True, "FIRST_DECISION")
    )
    orchestrator.register_rule(
        StubRule(True, "SECOND_DECISION")
    )
    orchestrator.register_rule(
        StubRule(True, "THIRD_DECISION")
    )

    decisions = orchestrator.decide({})

    assert len(decisions) == 1


def test_orchestrator_preserves_registration_order():
    orchestrator = DiagnosticDecisionOrchestrator()

    first_rule = StubRule(False, "FIRST_DECISION")
    second_rule = StubRule(True, "SECOND_DECISION")

    orchestrator.register_rule(first_rule)
    orchestrator.register_rule(second_rule)

    decisions = orchestrator.decide({})

    assert len(decisions) == 1
    assert decisions[0].decision_type == "SECOND_DECISION"


def test_orchestrator_rejects_invalid_rule():
    orchestrator = DiagnosticDecisionOrchestrator()

    try:
        orchestrator.register_rule(object())
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_orchestrator_rejects_non_dictionary_evidence():
    orchestrator = DiagnosticDecisionOrchestrator()

    try:
        orchestrator.decide([])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")