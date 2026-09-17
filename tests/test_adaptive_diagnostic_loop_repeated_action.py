from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome

class RepeatingDecisionEngine:
    def __init__(self):
        self.calls = 0

    def decide(self, evidence):
        self.calls += 1

        return [
            type(
                "StubDecision",
                (),
                {
                    "decision_type": "CHECK_GATEWAY_REACHABILITY"
                },
            )()
        ]


class StubActionSelector:
    def select(self, decision_type):
        return DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Check whether the default gateway is reachable.",
        )


class StableExecutor:
    def __init__(self):
        self.calls = 0

    def execute(self, action):
        self.calls += 1

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence={
                "gateway_reachable": True,
            },
        )


def create_loop(executor):
    return AdaptiveDiagnosticLoop(
        decision_engine=RepeatingDecisionEngine(),
        action_selector=StubActionSelector(),
        executor=executor,
        max_steps=3,
    )


def test_loop_respects_max_steps_when_same_decision_repeats():
    executor = StableExecutor()

    loop = create_loop(executor)

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.steps == 3


def test_loop_does_not_execute_beyond_max_steps_when_action_repeats():
    executor = StableExecutor()

    loop = create_loop(executor)

    loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert executor.calls == 3


def test_repeated_action_is_recorded_as_each_executed_step():
    executor = StableExecutor()

    loop = create_loop(executor)

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.actions == [
        "PING_DEFAULT_GATEWAY",
        "PING_DEFAULT_GATEWAY",
        "PING_DEFAULT_GATEWAY",
    ]


def test_repeated_action_does_not_create_diagnostic_findings():
    executor = StableExecutor()

    loop = create_loop(executor)

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    result_data = result.to_dict()

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data