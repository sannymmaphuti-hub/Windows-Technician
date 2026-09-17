from engine.diagnostic_action import DiagnosticAction


def test_diagnostic_action_can_be_created():
    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    assert action is not None


def test_diagnostic_action_requires_action_type():
    try:
        DiagnosticAction(
            action_type="",
            category="NETWORK",
            description="Check the default gateway.",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_requires_category():
    try:
        DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="",
            description="Check the default gateway.",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_requires_description():
    try:
        DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_rejects_non_string_action_type():
    try:
        DiagnosticAction(
            action_type=123,
            category="NETWORK",
            description="Check the default gateway.",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_rejects_non_string_category():
    try:
        DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category=123,
            description="Check the default gateway.",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_rejects_non_string_description():
    try:
        DiagnosticAction(
            action_type="PING_DEFAULT_GATEWAY",
            category="NETWORK",
            description=123,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_diagnostic_action_to_dict():
    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    assert action.to_dict() == {
        "action_type": "PING_DEFAULT_GATEWAY",
        "category": "NETWORK",
        "description": "Check whether the default gateway is reachable.",
    }