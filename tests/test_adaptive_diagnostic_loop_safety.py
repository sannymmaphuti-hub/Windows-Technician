from engine.diagnostic_action import DiagnosticAction
from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class StubDecision:
    def __init__(self, decision_type):
        self.decision_type = decision_type


class StubDecisionEngine:
    def __init__(self):
        self.calls = 0

    def decide(self, evidence):
        self.calls += 1

        return [
            StubDecision("CHECK_GATEWAY_REACHABILITY")
        ]


class StubActionSelector:
    def __init__(self):
        self.calls = 0

    def select(self, decision_type):
        self.calls += 1

        return DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Stub diagnostic action.",
        )


class StubExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, action):
        self.calls.append(action)

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence={
                "gateway_reachable": True,
            },
        )


def create_loop(max_steps=100):
    return AdaptiveDiagnosticLoop(
        StubDecisionEngine(),
        StubActionSelector(),
        StubExecutor(),
        max_steps=max_steps,
    )


def test_loop_accepts_max_steps():
    loop = create_loop(max_steps=3)

    assert loop.max_steps == 3


def test_loop_rejects_invalid_max_steps():
    try:
        AdaptiveDiagnosticLoop(
            StubDecisionEngine(),
            StubActionSelector(),
            StubExecutor(),
            max_steps=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_loop_stops_when_max_steps_is_reached():
    loop = create_loop(max_steps=3)

    result = loop.run({})

    assert isinstance(result, AdaptiveDiagnosticResult)
    assert result.steps == 3
    assert result.stopped_reason == "MAX_STEPS"


def test_loop_does_not_execute_beyond_max_steps():
    decision_engine = StubDecisionEngine()
    action_selector = StubActionSelector()
    executor = StubExecutor()

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
        max_steps=2,
    )

    result = loop.run({})

    assert result.steps == 2
    assert decision_engine.calls == 2
    assert action_selector.calls == 2
    assert len(executor.calls) == 2