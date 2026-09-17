from engine.diagnostic_decision import DiagnosticDecision


def test_diagnostic_decision_can_be_created():
    decision = DiagnosticDecision(
        decision_type="CHECK_GATEWAY_REACHABILITY",
        category="NETWORK",
        reason="Gateway reachability is unknown.",
        priority="HIGH",
    )

    assert decision.decision_type == "CHECK_GATEWAY_REACHABILITY"
    assert decision.category == "NETWORK"
    assert decision.reason == "Gateway reachability is unknown."
    assert decision.priority == "HIGH"


def test_diagnostic_decision_requires_decision_type():
    try:
        DiagnosticDecision(
            decision_type="",
            category="NETWORK",
            reason="Gateway reachability is unknown.",
            priority="HIGH",
        )
    except ValueError:
        return

    assert False, "Expected ValueError for empty decision_type"


def test_diagnostic_decision_requires_category():
    try:
        DiagnosticDecision(
            decision_type="CHECK_GATEWAY_REACHABILITY",
            category="",
            reason="Gateway reachability is unknown.",
            priority="HIGH",
        )
    except ValueError:
        return

    assert False, "Expected ValueError for empty category"


def test_diagnostic_decision_requires_reason():
    try:
        DiagnosticDecision(
            decision_type="CHECK_GATEWAY_REACHABILITY",
            category="NETWORK",
            reason="",
            priority="HIGH",
        )
    except ValueError:
        return

    assert False, "Expected ValueError for empty reason"


def test_diagnostic_decision_requires_valid_priority():
    try:
        DiagnosticDecision(
            decision_type="CHECK_GATEWAY_REACHABILITY",
            category="NETWORK",
            reason="Gateway reachability is unknown.",
            priority="INVALID",
        )
    except ValueError:
        return

    assert False, "Expected ValueError for invalid priority"


def test_diagnostic_decision_accepts_valid_priorities():
    for priority in {"LOW", "MEDIUM", "HIGH"}:
        decision = DiagnosticDecision(
            decision_type="CHECK_GATEWAY_REACHABILITY",
            category="NETWORK",
            reason="Gateway reachability is unknown.",
            priority=priority,
        )

        assert decision.priority == priority


def test_diagnostic_decision_to_dict():
    decision = DiagnosticDecision(
        decision_type="CHECK_GATEWAY_REACHABILITY",
        category="NETWORK",
        reason="Gateway reachability is unknown.",
        priority="HIGH",
    )

    assert decision.to_dict() == {
        "decision_type": "CHECK_GATEWAY_REACHABILITY",
        "category": "NETWORK",
        "reason": "Gateway reachability is unknown.",
        "priority": "HIGH",
    }