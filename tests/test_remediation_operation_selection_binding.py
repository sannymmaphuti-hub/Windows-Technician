from engine.remediation_action import RemediationAction
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)
from engine.remediation_operation_selector import (
    RemediationOperationSelector,
)
from engine.remediation_operation_binder import (
    RemediationOperationBinder,
)


def test_selected_operation_can_be_bound():
    registry = RemediationOperationRegistry()

    operation = lambda: None
    registry.register("memory_review", operation)

    selector = RemediationOperationSelector()
    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    binder.bind(action, operation_id)

    assert action.operation is operation


def test_selection_does_not_bind_automatically():
    registry = RemediationOperationRegistry()

    operation = lambda: None
    registry.register("memory_review", operation)

    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_002",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    assert operation_id == "memory_review"
    assert action.operation is None


def test_unsupported_selection_cannot_be_bound():
    registry = RemediationOperationRegistry()

    binder = RemediationOperationBinder(registry)
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_003",
        description="Investigate CPU usage.",
        category="CPU",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    assert operation_id is None

    try:
        binder.bind(action, operation_id)
    except ValueError:
        pass

    assert action.operation is None


def test_binding_does_not_execute_operation():
    registry = RemediationOperationRegistry()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    registry.register("memory_review", operation)

    selector = RemediationOperationSelector()
    binder = RemediationOperationBinder(registry)

    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    operation_id = selector.select(action)
    binder.bind(action, operation_id)

    assert action.operation is operation
    assert state["executed"] is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"