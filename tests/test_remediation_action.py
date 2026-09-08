
from engine.remediation_action import RemediationAction


def test_remediation_action_can_be_created():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    assert action.action_id == "test_action"
    assert action.description == "Test remediation action"


def test_remediation_action_requires_authorization_by_default():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    assert action.requires_authorization is True


def test_remediation_action_starts_unauthorized():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    assert action.authorization_status == "UNAUTHORIZED"


def test_remediation_action_starts_unexecuted():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    assert action.execution_status == "NOT_EXECUTED"

def test_remediation_action_can_be_authorized():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_remediation_action_can_be_denied():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    action.deny()

    assert action.authorization_status == "DENIED"


def test_authorizing_action_does_not_execute_it():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_remains_unexecuted():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_unauthorized_action_cannot_execute():
    executed = []

    def operation():
        executed.append(True)

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    result = action.execute()

    assert result is False
    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"


def test_authorized_action_can_execute_operation():
    executed = []

    def operation():
        executed.append(True)

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is True
    assert executed == [True]
    assert action.execution_status == "EXECUTED"


def test_execution_does_not_happen_during_authorization():
    executed = []

    def operation():
        executed.append(True)

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.authorize()

    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"

def test_failed_operation_sets_execution_status_to_failed():
    def operation():
        raise RuntimeError("Operation failed")

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is False
    assert action.execution_status == "FAILED"


def test_failed_operation_does_not_escape_as_exception():
    def operation():
        raise RuntimeError("Operation failed")

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is False


def test_successful_operation_keeps_executed_status():
    def operation():
        return None

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is True
    assert action.execution_status == "EXECUTED"

def test_denied_action_cannot_execute():
    executed = []

    def operation():
        executed.append(True)

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        operation=operation,
    )

    action.deny()

    result = action.execute()

    assert result is False
    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"

def test_action_without_authorization_requirement_can_execute():
    executed = []

    def operation():
        executed.append(True)

    action = RemediationAction(
        action_id="test_action",
        description="Test remediation action",
        requires_authorization=False,
        operation=operation,
    )

    result = action.execute()

    assert result is True
    assert executed == [True]
    assert action.execution_status == "EXECUTED"

def test_equivalent_actions_compare_equal():
    action_one = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        category="memory",
        severity="WARNING",
    )

    action_two = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        category="memory",
        severity="WARNING",
    )

    assert action_one == action_two

def test_executed_action_cannot_execute_again():
    executed = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executed.append("run"),
    )

    action.authorize()

    assert action.execute() is True
    assert executed == ["run"]

    assert action.execute() is False
    assert executed == ["run"]

def test_failed_action_cannot_execute_again():
    attempts = []

    def failing_operation():
        attempts.append("run")
        raise RuntimeError("operation failed")

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=failing_operation,
    )

    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"
    assert attempts == ["run"]

    assert action.execute() is False
    assert attempts == ["run"]