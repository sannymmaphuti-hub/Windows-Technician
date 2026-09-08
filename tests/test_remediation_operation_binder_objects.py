from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_operation_binder import (
    RemediationOperationBinder,
)
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)


def test_binder_can_bind_remediation_operation_object():
    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    registry.register(
        operation.operation_id,
        operation,
    )

    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    binder.bind(action, "memory_review")

    assert action.operation is operation


def test_binder_preserves_operation_object_state():
    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    registry.register(
        "memory_review",
        operation,
    )

    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_002",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    binder.bind(action, "memory_review")

    assert action.operation.execution_status == "NOT_EXECUTED"


def test_binder_does_not_execute_operation_object():
    state = {"executed": False}

    def handler():
        state["executed"] = True

    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    registry.register(
        "memory_review",
        operation,
    )

    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_003",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    binder.bind(action, "memory_review")

    assert state["executed"] is False
    assert action.execution_status == "NOT_EXECUTED"


def test_binder_preserves_action_authorization_state():
    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    registry.register(
        "memory_review",
        operation,
    )

    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    action.deny()

    binder.bind(action, "memory_review")

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.operation is operation