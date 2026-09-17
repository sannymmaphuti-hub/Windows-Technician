from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class StubDecision:
    def __init__(self, decision_type):
        self.decision_type = decision_type


class StubDecisionEngine:
    def __init__(self):
        self.call_count = 0

    def decide(self, evidence):
        self.call_count += 1

        if self.call_count == 1:
            return [
                StubDecision("CHECK_GATEWAY_REACHABILITY")
            ]

        return []


class StubActionSelector:
    def select(self, decision_type):
        return DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="Check whether the default gateway is reachable.",
        )


class ConflictingEvidenceExecutor:
    def execute(self, action):
        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence={
                "gateway_reachable": False,
            },
        )

def create_loop():
    return AdaptiveDiagnosticLoop(
        decision_engine=StubDecisionEngine(),
        action_selector=StubActionSelector(),
        executor=ConflictingEvidenceExecutor(),
    )


def test_loop_records_latest_evidence_when_key_is_repeated():
    loop = create_loop()

    result = loop.run(
        {
            "gateway_reachable": True,
        }
    )

    assert result.evidence["gateway_reachable"] is False


def test_loop_completes_when_conflicting_evidence_is_returned():
    loop = create_loop()

    result = loop.run(
        {
            "gateway_reachable": True,
        }
    )

    assert result.stopped_reason == "NO_DECISION"


def test_loop_does_not_create_duplicate_evidence_keys():
    loop = create_loop()

    result = loop.run(
        {
            "gateway_reachable": True,
        }
    )

    assert list(result.evidence.keys()).count(
        "gateway_reachable"
    ) == 1


def test_conflicting_evidence_does_not_create_findings():
    loop = create_loop()

    result = loop.run(
        {
            "gateway_reachable": True,
        }
    )

    result_data = result.to_dict()

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data