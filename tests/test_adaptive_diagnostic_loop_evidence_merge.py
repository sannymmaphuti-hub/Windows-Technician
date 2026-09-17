from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome

class StubDecisionEngine:
    def __init__(self, decisions):
        self.decisions = list(decisions)

    def decide(self, evidence):
        if not self.decisions:
            return []

        return [self.decisions.pop(0)]


class StubActionSelector:
    def __init__(self):
        self.calls = []

    def select(self, decision_type):
        self.calls.append(decision_type)

        return DiagnosticAction(
            action_type="TEST_OPERATION",
            category="NETWORK",
            description="Test diagnostic operation.",
        )


class StubExecutor:
    def __init__(self, evidence):
        self.evidence = evidence
        self.calls = 0
    def execute(self, action):
        self.calls += 1

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence=dict(self.evidence),
        )

class StubDecision:
    def __init__(self, decision_type):
        self.decision_type = decision_type


def test_loop_preserves_existing_evidence_when_new_evidence_has_different_keys():
    decision_engine = StubDecisionEngine(
        [
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
        ]
    )

    action_selector = StubActionSelector()

    executor = StubExecutor(
        {
            "gateway_reachable": True,
        }
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=executor,
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.evidence["active_adapter"]["is_up"] is True
    assert result.evidence["gateway_reachable"] is True


def test_loop_accepts_new_evidence_keys():
    decision_engine = StubDecisionEngine(
        [
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
        ]
    )

    action_selector = StubActionSelector()

    executor = StubExecutor(
        {
            "gateway_reachable": True,
        }
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=executor,
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.evidence == {
        "active_adapter": {
            "is_up": True,
        },
        "gateway_reachable": True,
    }


def test_loop_does_not_lose_unrelated_existing_evidence():
    decision_engine = StubDecisionEngine(
        [
            StubDecision("CHECK_DNS_RESOLUTION"),
        ]
    )

    action_selector = StubActionSelector()

    executor = StubExecutor(
        {
            "dns_working": True,
        }
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=executor,
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
            "gateway_reachable": True,
        }
    )

    assert result.evidence["active_adapter"]["is_up"] is True
    assert result.evidence["gateway_reachable"] is True
    assert result.evidence["dns_working"] is True


def test_loop_rejects_non_dictionary_new_evidence():
    decision_engine = StubDecisionEngine(
        [
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
        ]
    )

    action_selector = StubActionSelector()

    class InvalidExecutor:
        def execute(self, action):
            return "invalid evidence"

    loop = AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=InvalidExecutor(),
    )

    try:
        loop.run(
            {
                "active_adapter": {
                    "is_up": True,
                }
            }
        )
    except ValueError as error:
        assert str(error) == (
            "diagnostic executor must return a DiagnosticActionOutcome."
        )
    else:
        raise AssertionError(
            "Expected ValueError for non-dictionary evidence."
        )


def test_loop_does_not_execute_when_no_decision_exists():
    decision_engine = StubDecisionEngine([])

    action_selector = StubActionSelector()

    executor = StubExecutor(
        {
            "unexpected": True,
        }
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=executor,
    )

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.steps == 0
    assert executor.calls == 0
    assert result.evidence == {
        "active_adapter": {
            "is_up": True,
        }
    }