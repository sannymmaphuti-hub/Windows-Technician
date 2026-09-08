from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation


def test_action_can_execute_remediation_operation_object():
    state = {"executed": False}

    def handler():
        state["executed"] = True

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is True
    assert state["executed"] is True
    assert action.execution_status == "EXECUTED"


def test_action_execution_does_not_execute_unauthorized_operation_object():
    state = {"executed": False}

    def handler():
        state["executed"] = True

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    action = RemediationAction(
        action_id="action_002",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    result = action.execute()

    assert result is False
    assert state["executed"] is False
    assert action.execution_status == "NOT_EXECUTED"


def test_action_records_failed_operation_object():
    def handler():
        raise RuntimeError("operation failed")

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    action = RemediationAction(
        action_id="action_003",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is False
    assert action.execution_status == "FAILED"

def test_failed_operation_object_records_failed_status():
    def handler():
        raise RuntimeError("operation failed")

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    result = action.execute()

    assert result is False
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"