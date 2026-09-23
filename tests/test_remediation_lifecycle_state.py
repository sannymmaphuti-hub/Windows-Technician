# ==========================================
# Windows Technician v0.6
# REMEDIATION LIFECYCLE STATE
# ==========================================

from engine.remediation_action import RemediationAction


def create_action():
    return RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )


def test_new_action_starts_in_not_executed_state():
    action = create_action()

    assert action.execution_status == "NOT_EXECUTED"


def test_new_action_starts_unauthorized():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_authorizing_action_changes_authorization_state():
    action = create_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_denying_action_changes_authorization_state():
    action = create_action()

    action.deny()

    assert action.authorization_status == "DENIED"


def test_authorized_action_can_be_executed_when_operation_is_bound():
    action = create_action()
    action.operation = lambda: None
    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"


def test_unauthorized_action_cannot_execute():
    action = create_action()
    action.operation = lambda: None

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_denied_action_cannot_execute():
    action = create_action()
    action.operation = lambda: None
    action.deny()

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_action_cannot_execute_after_success():
    action = create_action()
    action.operation = lambda: None
    action.authorize()

    assert action.execute() is True
    assert action.execute() is False
    assert action.execution_status == "EXECUTED"


def test_failed_action_becomes_terminal():
    def failing_operation():
        raise RuntimeError("test failure")

    action = create_action()
    action.operation = failing_operation
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"


def test_failed_action_cannot_execute_again():
    def failing_operation():
        raise RuntimeError("test failure")

    action = create_action()
    action.operation = failing_operation
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"

    assert action.execute() is False
    assert action.execution_status == "FAILED"


def test_authorization_does_not_execute_action():
    executed = []

    def operation():
        executed.append(True)

    action = create_action()
    action.operation = operation

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []


def test_denying_action_does_not_execute_action():
    executed = []

    def operation():
        executed.append(True)

    action = create_action()
    action.operation = operation

    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []
    
def test_denied_action_cannot_be_authorized():
    action = create_action()

    action.deny()

    action.authorize()

    assert action.authorization_status == "DENIED"


def test_executed_action_cannot_be_authorized_again():
    action = create_action()
    action.operation = lambda: None
    action.authorize()

    assert action.execute() is True

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"


def test_failed_action_cannot_be_authorized_again():
    def failing_operation():
        raise RuntimeError("test failure")

    action = create_action()
    action.operation = failing_operation
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "FAILED"

def test_authorized_action_can_be_denied_before_execution():
    action = create_action()

    action.authorize()
    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"

def test_binding_operation_does_not_authorize_action():
    action = create_action()

    action.operation = lambda: None

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_binding_operation_does_not_execute_action():
    executed = []

    def operation():
        executed.append(True)

    action = create_action()
    action.operation = operation

    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []


def test_bound_action_requires_authorization_before_execution():
    executed = []

    def operation():
        executed.append(True)

    action = create_action()
    action.operation = operation

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []


def test_binding_then_authorizing_allows_execution():
    executed = []

    def operation():
        executed.append(True)

    action = create_action()
    action.operation = operation

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"
    assert executed == [True]

def test_successful_action_cannot_be_denied_after_execution():
    action = create_action()
    action.operation = lambda: None
    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"

    action.deny()

    assert action.execution_status == "EXECUTED"
    assert action.authorization_status == "AUTHORIZED"


def test_failed_action_cannot_be_denied_after_failure():
    def failing_operation():
        raise RuntimeError("test failure")

    action = create_action()
    action.operation = failing_operation
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"

    action.deny()

    assert action.execution_status == "FAILED"
    assert action.authorization_status == "AUTHORIZED"


def test_successful_action_cannot_replace_operation():
    first_operation = lambda: None
    second_operation = lambda: None

    action = create_action()
    action.operation = first_operation
    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"

    action.operation = second_operation

    assert action.execution_status == "EXECUTED"
    assert action.operation is first_operation


def test_failed_action_cannot_replace_operation():
    def failing_operation():
        raise RuntimeError("test failure")

    second_operation = lambda: None

    action = create_action()
    action.operation = failing_operation
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"

    action.operation = second_operation

    assert action.execution_status == "FAILED"
    assert action.operation is failing_operation

