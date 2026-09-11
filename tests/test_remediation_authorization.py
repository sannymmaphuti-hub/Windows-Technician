from engine.remediation_action import RemediationAction


def test_new_action_starts_unauthorized():
    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    assert action.authorization_status == "UNAUTHORIZED"


def test_action_can_be_explicitly_authorized():
    action = RemediationAction(
        action_id="action_002",
        description="Review memory usage.",
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_authorization_does_not_execute_action():
    action = RemediationAction(
        action_id="action_003",
        description="Review memory usage.",
        operation=lambda: None,
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_bind_operation():
    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.operation is None


def test_denied_action_cannot_be_authorized():
    action = RemediationAction(
        action_id="action_005",
        description="Review memory usage.",
    )

    action.deny()
    action.authorize()

    assert action.authorization_status == "DENIED"

def test_authorized_action_can_be_denied_before_execution():
    action = RemediationAction(
        action_id="action_006",
        description="Review memory usage.",
    )

    action.authorize()
    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"

def test_unauthorized_action_cannot_execute_directly():
    executed = False

    def operation():
        nonlocal executed
        executed = True

    action = RemediationAction(
        action_id="action_007",
        description="Review memory usage.",
        operation=operation,
    )

    result = action.execute()

    assert result is False
    assert executed is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_action_without_authorization_requirement_can_execute():
    executed = False

    def operation():
        nonlocal executed
        executed = True

    action = RemediationAction(
        action_id="action_008",
        description="Non-sensitive test operation.",
        requires_authorization=False,
        operation=operation,
    )

    result = action.execute()

    assert result is True
    assert executed is True
    assert action.execution_status == "EXECUTED"