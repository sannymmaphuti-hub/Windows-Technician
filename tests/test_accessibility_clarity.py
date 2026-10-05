from engine.accessibility_clarity import AccessibilityClarity


def test_accessibility_clarity_can_be_created():
    clarity = AccessibilityClarity()

    assert clarity is not None


def test_unauthorized_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.authorization_label(
        "UNAUTHORIZED"
    ) == "Authorization required"


def test_authorized_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.authorization_label(
        "AUTHORIZED"
    ) == "Authorized"


def test_denied_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.authorization_label(
        "DENIED"
    ) == "Denied"


def test_not_executed_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.execution_label(
        "NOT_EXECUTED"
    ) == "Not executed"


def test_executed_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.execution_label(
        "EXECUTED"
    ) == "Executed"


def test_failed_label_is_clear():
    clarity = AccessibilityClarity()

    assert clarity.execution_label(
        "FAILED"
    ) == "Failed"


def test_unknown_authorization_state_uses_safe_label():
    clarity = AccessibilityClarity()

    assert clarity.authorization_label(
        "UNKNOWN"
    ) == "Unknown authorization state"


def test_unknown_execution_state_uses_safe_label():
    clarity = AccessibilityClarity()

    assert clarity.execution_label(
        "UNKNOWN"
    ) == "Unknown execution state"


def test_authorization_state_requires_string():
    clarity = AccessibilityClarity()

    try:
        clarity.authorization_label(None)
    except ValueError as error:
        assert str(error) == (
            "authorization_status must be a string."
        )


def test_execution_state_requires_string():
    clarity = AccessibilityClarity()

    try:
        clarity.execution_label(None)
    except ValueError as error:
        assert str(error) == (
            "execution_status must be a string."
        )


def test_empty_authorization_state_is_rejected():
    clarity = AccessibilityClarity()

    try:
        clarity.authorization_label("   ")
    except ValueError as error:
        assert str(error) == (
            "authorization_status cannot be empty."
        )


def test_empty_execution_state_is_rejected():
    clarity = AccessibilityClarity()

    try:
        clarity.execution_label("   ")
    except ValueError as error:
        assert str(error) == (
            "execution_status cannot be empty."
        )


def test_clarity_layer_does_not_authorize():
    clarity = AccessibilityClarity()

    assert not hasattr(clarity, "authorize")


def test_clarity_layer_does_not_execute():
    clarity = AccessibilityClarity()

    assert not hasattr(clarity, "execute")


def test_clarity_layer_does_not_remediate():
    clarity = AccessibilityClarity()

    assert not hasattr(clarity, "remediate")