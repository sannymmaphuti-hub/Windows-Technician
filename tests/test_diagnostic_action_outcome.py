from engine.diagnostic_action_outcome import DiagnosticActionOutcome


def test_diagnostic_action_outcome_can_be_created():
    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": True,
        },
    )

    assert outcome.action_type == "PING_DEFAULT_GATEWAY"
    assert outcome.evidence == {
        "gateway_reachable": True,
    }


def test_diagnostic_action_outcome_requires_action_type():
    try:
        DiagnosticActionOutcome(
            action_type="",
            evidence={
                "gateway_reachable": True,
            },
        )
    except ValueError as error:
        assert str(error) == (
            "action_type must be a non-empty string."
        )
    else:
        raise AssertionError(
            "Expected ValueError for empty action_type."
        )


def test_diagnostic_action_outcome_rejects_non_string_action_type():
    try:
        DiagnosticActionOutcome(
            action_type=123,
            evidence={
                "gateway_reachable": True,
            },
        )
    except ValueError as error:
        assert str(error) == (
            "action_type must be a non-empty string."
        )
    else:
        raise AssertionError(
            "Expected ValueError for non-string action_type."
        )


def test_diagnostic_action_outcome_requires_evidence_dictionary():
    try:
        DiagnosticActionOutcome(
            action_type="PING_DEFAULT_GATEWAY",
            evidence=None,
        )
    except ValueError as error:
        assert str(error) == (
            "evidence must be a dictionary."
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid evidence."
        )


def test_diagnostic_action_outcome_rejects_non_dictionary_evidence():
    try:
        DiagnosticActionOutcome(
            action_type="PING_DEFAULT_GATEWAY",
            evidence="gateway reachable",
        )
    except ValueError as error:
        assert str(error) == (
            "evidence must be a dictionary."
        )
    else:
        raise AssertionError(
            "Expected ValueError for non-dictionary evidence."
        )


def test_diagnostic_action_outcome_copies_evidence():
    evidence = {
        "gateway_reachable": True,
    }

    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence=evidence,
    )

    evidence["gateway_reachable"] = False

    assert outcome.evidence == {
        "gateway_reachable": True,
    }


def test_diagnostic_action_outcome_to_dict():
    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": True,
        },
    )

    assert outcome.to_dict() == {
        "action_type": "PING_DEFAULT_GATEWAY",
        "evidence": {
            "gateway_reachable": True,
        },
    }


def test_diagnostic_action_outcome_contains_only_diagnostic_outcome_data():
    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": True,
        },
    )

    result = outcome.to_dict()

    assert "findings" not in result
    assert "root_causes" not in result
    assert "recommendations" not in result
    assert "remediation" not in result