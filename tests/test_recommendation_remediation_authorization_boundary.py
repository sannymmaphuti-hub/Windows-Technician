from engine.remediation_action import RemediationAction


def create_action():
    return RemediationAction(
        action_id="test_memory_review",
        description="Review memory-intensive processes.",
        category="MEMORY",
        severity="WARNING",
    )


def test_new_remediation_action_starts_unauthorized():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_new_remediation_action_starts_not_executed():
    action = create_action()

    assert action.execution_status == "NOT_EXECUTED"


def test_new_remediation_action_has_no_operation():
    action = create_action()

    assert action.operation is None


def test_unauthorized_action_cannot_execute():
    action = create_action()

    result = action.execute()

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_is_explicit():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_authorization_alone_does_not_execute():
    action = create_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_operation_is_required_for_execution():
    action = create_action()

    action.authorize()

    result = action.execute()

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_create_operation():
    action = create_action()

    action.authorize()

    assert action.operation is None