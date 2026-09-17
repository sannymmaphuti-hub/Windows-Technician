from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome

class StubDecision:
    def __init__(self, decision_type):
        self.decision_type = decision_type


class StubDecisionEngine:
    def __init__(self, decisions):
        self.decisions = list(decisions)

    def decide(self, evidence):
        if not self.decisions:
            return []

        return [self.decisions.pop(0)]


class StubActionSelector:
    def select(self, decision_type):
        return DiagnosticAction(
            action_type="TEST_OPERATION",
            category="NETWORK",
            description="Run diagnostic test.",
        )


class StubExecutor:
    def __init__(self, evidence):
        self.evidence = evidence

    def execute(self, action):
        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence=dict(self.evidence),
        )


def test_loop_accepts_empty_new_evidence():
    loop = AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(
            [StubDecision("CHECK_GATEWAY_REACHABILITY")]
        ),
        action_selector=StubActionSelector(),
        executor=StubExecutor({}),
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            }
        }
    )

    assert result.evidence == {
        "active_adapter": {
            "is_up": True,
        }
    }


def test_loop_preserves_existing_evidence_when_new_evidence_is_empty():
    loop = AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(
            [StubDecision("CHECK_GATEWAY_REACHABILITY")]
        ),
        action_selector=StubActionSelector(),
        executor=StubExecutor({}),
    )

    result = loop.run(
        {
            "gateway_reachable": True,
        }
    )

    assert result.evidence["gateway_reachable"] is True


def test_loop_does_not_invent_missing_evidence_fields():
    loop = AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(
            [StubDecision("CHECK_GATEWAY_REACHABILITY")]
        ),
        action_selector=StubActionSelector(),
        executor=StubExecutor(
            {
                "gateway_reachable": True,
            }
        ),
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            }
        }
    )

    assert "dns_working" not in result.evidence
    assert "internet_reachable" not in result.evidence


def test_loop_preserves_partial_new_evidence():
    loop = AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(
            [StubDecision("CHECK_GATEWAY_REACHABILITY")]
        ),
        action_selector=StubActionSelector(),
        executor=StubExecutor(
            {
                "gateway_reachable": True,
            }
        ),
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
            "existing_value": "preserved",
        }
    )

    assert result.evidence == {
        "active_adapter": {
            "is_up": True,
        },
        "existing_value": "preserved",
        "gateway_reachable": True,
    }