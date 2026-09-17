from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult


def test_result_can_be_created():
    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=0,
        stopped_reason="NO_DECISION",
    )

    assert result is not None


def test_result_preserves_final_evidence():
    result = AdaptiveDiagnosticResult(
        evidence={
            "gateway_reachable": True,
        },
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    assert result.evidence == {
        "gateway_reachable": True,
    }


def test_result_preserves_decisions():
    decisions = [
        "CHECK_GATEWAY_REACHABILITY",
        "CHECK_DNS_RESOLUTION",
    ]

    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=decisions,
        actions=[],
        steps=2,
        stopped_reason="NO_DECISION",
    )

    assert result.decisions == decisions


def test_result_preserves_actions():
    actions = [
        "PING_DEFAULT_GATEWAY",
        "TEST_DNS_RESOLUTION",
    ]

    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=actions,
        steps=2,
        stopped_reason="NO_DECISION",
    )

    assert result.actions == actions


def test_result_preserves_step_count():
    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=4,
        stopped_reason="NO_DECISION",
    )

    assert result.steps == 4


def test_result_preserves_stop_reason():
    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=4,
        stopped_reason="NO_DECISION",
    )

    assert result.stopped_reason == "NO_DECISION"


def test_result_supports_safety_limit_stop_reason():
    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=3,
        stopped_reason="MAX_STEPS",
    )

    assert result.stopped_reason == "MAX_STEPS"


def test_result_rejects_invalid_evidence():
    try:
        AdaptiveDiagnosticResult(
            evidence=None,
            decisions=[],
            actions=[],
            steps=0,
            stopped_reason="NO_DECISION",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_result_rejects_invalid_step_count():
    try:
        AdaptiveDiagnosticResult(
            evidence={},
            decisions=[],
            actions=[],
            steps=-1,
            stopped_reason="NO_DECISION",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_result_to_dict():
    result = AdaptiveDiagnosticResult(
        evidence={
            "gateway_reachable": True,
        },
        decisions=[
            "CHECK_GATEWAY_REACHABILITY",
        ],
        actions=[
            "PING_DEFAULT_GATEWAY",
        ],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    assert result.to_dict() == {
        "evidence": {
            "gateway_reachable": True,
        },
        "decisions": [
            "CHECK_GATEWAY_REACHABILITY",
        ],
        "actions": [
            "PING_DEFAULT_GATEWAY",
        ],
        "steps": 1,
        "stopped_reason": "NO_DECISION",
    }

def test_result_preserves_observations():
    observations = [
        "gateway_observation",
        "dns_observation",
    ]

    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=2,
        stopped_reason="NO_DECISION",
        observations=observations,
    )

    assert result.observations == observations


def test_result_copies_observations():
    observations = [
        "gateway_observation",
    ]

    result = AdaptiveDiagnosticResult(
        evidence={},
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
        observations=observations,
    )

    observations.append("dns_observation")

    assert result.observations == [
        "gateway_observation",
    ]


def test_result_rejects_invalid_observations():
    try:
        AdaptiveDiagnosticResult(
            evidence={},
            decisions=[],
            actions=[],
            steps=0,
            stopped_reason="NO_DECISION",
            observations=None,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_result_to_dict_includes_observations():
    result = AdaptiveDiagnosticResult(
        evidence={
            "gateway_reachable": True,
        },
        decisions=[
            "CHECK_GATEWAY_REACHABILITY",
        ],
        actions=[
            "PING_DEFAULT_GATEWAY",
        ],
        steps=1,
        stopped_reason="NO_DECISION",
        observations=[
            "gateway_observation",
        ],
    )

    assert result.to_dict() == {
        "evidence": {
            "gateway_reachable": True,
        },
        "decisions": [
            "CHECK_GATEWAY_REACHABILITY",
        ],
        "actions": [
            "PING_DEFAULT_GATEWAY",
        ],
        "steps": 1,
        "stopped_reason": "NO_DECISION",
        "observations": [
            "gateway_observation",
        ],
    }