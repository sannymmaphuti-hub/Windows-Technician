from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class StubDecisionEngine:
    def __init__(self):
        self.calls = []

    def decide(self, evidence):
        self.calls.append(dict(evidence))

        if "gateway_reachable" not in evidence:
            return [
                type(
                    "Decision",
                    (),
                    {
                        "decision_type": "CHECK_GATEWAY_REACHABILITY",
                    },
                )()
            ]

        return []


class StubActionSelector:
    def select(self, decision_type):
        return DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Check whether the default gateway is reachable.",
        )


class StubExecutor:
    def execute(self, action):
        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence={
                "gateway_reachable": True,
            },
        )


def create_loop():
    return AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(),
        action_selector=StubActionSelector(),
        executor=StubExecutor(),
    )


def test_loop_accepts_diagnostic_action_outcome():
    loop = create_loop()

    result = loop.run({})

    assert isinstance(result, AdaptiveDiagnosticResult)


def test_loop_merges_outcome_evidence():
    loop = create_loop()

    result = loop.run({})

    assert result.evidence == {
        "gateway_reachable": True,
    }


def test_loop_records_decision_and_action_from_outcome():
    loop = create_loop()

    result = loop.run({})

    assert result.decisions == [
        "CHECK_GATEWAY_REACHABILITY",
    ]

    assert result.actions == [
        "PING_DEFAULT_GATEWAY",
    ]


def test_loop_stops_after_outcome_evidence_resolves_decision():
    loop = create_loop()

    result = loop.run({})

    assert result.steps == 1
    assert result.stopped_reason == "NO_DECISION"


def test_loop_does_not_treat_outcome_as_diagnostic_conclusion():
    loop = create_loop()

    result = loop.run({})

    result_data = result.to_dict()

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data


def test_loop_requires_diagnostic_action_outcome():
    class InvalidExecutor:
        def execute(self, action):
            return {
                "gateway_reachable": True,
            }

    loop = AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(),
        action_selector=StubActionSelector(),
        executor=InvalidExecutor(),
    )

    try:
        loop.run({})
    except ValueError as error:
        assert str(error) == (
            "diagnostic executor must return a DiagnosticActionOutcome."
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid diagnostic executor result."
        )