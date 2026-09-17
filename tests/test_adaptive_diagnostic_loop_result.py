
from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class StubDecision:
    def __init__(self, decision_type):
        self.decision_type = decision_type


class StubDecisionEngine:
    def __init__(self, decisions):
        self.decisions = list(decisions)

    def decide(self, evidence):
        if self.decisions:
            return [self.decisions.pop(0)]

        return []


class StubAction:
    def __init__(self, action_type):
        self.action_type = action_type


class StubActionSelector:
    def select(self, decision_type):
        return StubAction(
            f"ACTION_FOR_{decision_type}"
        )


class StubExecutor:
    def __init__(self, evidence_results):
        self.evidence_results = list(evidence_results)
        self.calls = []

    def execute(self, action):
        self.calls.append(action)

        evidence = self.evidence_results.pop(0)

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence=evidence,
        )


def create_loop(decisions, evidence_results, max_steps=100):
    return AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(decisions),
        action_selector=StubActionSelector(),
        executor=StubExecutor(evidence_results),
        max_steps=max_steps,
    )


def test_loop_returns_adaptive_diagnostic_result():
    loop = create_loop(
        decisions=[],
        evidence_results=[],
    )

    result = loop.run({})

    assert isinstance(result, AdaptiveDiagnosticResult)


def test_loop_result_preserves_final_evidence():
    loop = create_loop(
        decisions=[
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
        ],
        evidence_results=[
            {"gateway_reachable": True},
        ],
    )

    result = loop.run({})

    assert result.evidence == {
        "gateway_reachable": True,
    }


def test_loop_result_records_decisions():
    loop = create_loop(
        decisions=[
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
            StubDecision("CHECK_DNS_RESOLUTION"),
        ],
        evidence_results=[
            {"gateway_reachable": True},
            {"dns_working": True},
        ],
    )

    result = loop.run({})

    assert result.decisions == [
        "CHECK_GATEWAY_REACHABILITY",
        "CHECK_DNS_RESOLUTION",
    ]


def test_loop_result_records_actions():
    loop = create_loop(
        decisions=[
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
            StubDecision("CHECK_DNS_RESOLUTION"),
        ],
        evidence_results=[
            {"gateway_reachable": True},
            {"dns_working": True},
        ],
    )

    result = loop.run({})

    assert result.actions == [
        "ACTION_FOR_CHECK_GATEWAY_REACHABILITY",
        "ACTION_FOR_CHECK_DNS_RESOLUTION",
    ]


def test_loop_result_records_step_count():
    loop = create_loop(
        decisions=[
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
            StubDecision("CHECK_DNS_RESOLUTION"),
        ],
        evidence_results=[
            {"gateway_reachable": True},
            {"dns_working": True},
        ],
    )

    result = loop.run({})

    assert result.steps == 2


def test_loop_result_records_normal_stop_reason():
    loop = create_loop(
        decisions=[],
        evidence_results=[],
    )

    result = loop.run({})

    assert result.stopped_reason == "NO_DECISION"


def test_loop_result_records_max_steps_stop_reason():
    loop = create_loop(
        decisions=[
            StubDecision("CHECK_GATEWAY_REACHABILITY"),
            StubDecision("CHECK_DNS_RESOLUTION"),
        ],
        evidence_results=[
            {"gateway_reachable": True},
        ],
        max_steps=1,
    )

    result = loop.run({})

    assert result.stopped_reason == "MAX_STEPS"


def test_loop_result_contains_only_diagnostic_process_data():
    loop = create_loop(
        decisions=[],
        evidence_results=[],
    )

    result = loop.run({})

    result_data = result.to_dict()

    assert set(result_data.keys()) == {
        "evidence",
        "decisions",
        "actions",
        "steps",
        "stopped_reason",
        "observations",
    }
    assert result_data["observations"] == []

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data

