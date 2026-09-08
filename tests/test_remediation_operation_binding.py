from engine.remediation_action import RemediationAction
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)
from engine.remediation_operation_binder import (
    RemediationOperationBinder,
)
import pytest

def test_registered_operation_can_be_bound_to_action():
    registry = RemediationOperationRegistry()

    operation = lambda: None

    registry.register(
        "memory_review",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    assert action.operation is None

    registered_operation = registry.get("memory_review")

    action.operation = registered_operation

    assert action.operation is operation

def test_binder_can_bind_registered_operation_to_action():
    registry = RemediationOperationRegistry()

    operation = lambda: None

    registry.register(
        "memory_review",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    binder = RemediationOperationBinder(
        registry=registry,
    )

    binder.bind(
        action=action,
        operation_id="memory_review",
    )

    assert action.operation is operation

def test_binder_rejects_unregistered_operation():
    registry = RemediationOperationRegistry()

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    binder = RemediationOperationBinder(
        registry=registry,
    )

    with pytest.raises(ValueError):
        binder.bind(
            action=action,
            operation_id="unknown_operation",
        )

    assert action.operation is None

def test_binder_does_not_execute_operation():
    registry = RemediationOperationRegistry()

    state = {
        "executed": False,
    }

    def operation():
        state["executed"] = True

    registry.register(
        "memory_review",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    binder = RemediationOperationBinder(
        registry=registry,
    )

    binder.bind(
        action=action,
        operation_id="memory_review",
    )

    assert action.operation is operation
    assert state["executed"] is False