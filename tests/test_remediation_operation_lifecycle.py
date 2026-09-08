from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_operation_binder import RemediationOperationBinder
from engine.remediation_operation_registry import RemediationOperationRegistry
from engine.remediation_coordinator import RemediationCoordinator


def test_unauthorized_operation_does_not_execute():
    executed = []

    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
        handler=lambda: executed.append(True),
    )

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    coordinator = RemediationCoordinator()

    result = coordinator.execute(action)

    assert result.execution_status != "EXECUTED"
    assert action.execution_status != "EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"
    assert executed == []


def test_failed_operation_propagates_failed_status():
    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
        handler=lambda: (_ for _ in ()).throw(
            RuntimeError("operation failed")
        ),
    )

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    coordinator = RemediationCoordinator()

    result = coordinator.execute(action)

    assert result.execution_status == "FAILED"
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"


def test_failed_action_cannot_execute_again():
    executions = []

    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
        handler=lambda: (
            executions.append(True),
            (_ for _ in ()).throw(
                RuntimeError("operation failed")
            ),
        ),
    )

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    coordinator = RemediationCoordinator()

    first_result = coordinator.execute(action)
    second_result = coordinator.execute(action)

    assert first_result.execution_status == "FAILED"
    assert second_result.execution_status == "FAILED"
    assert len(executions) == 1


def test_successful_operation_can_be_verified():
    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
        handler=lambda: None,
    )

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=operation,
    )

    action.authorize()

    coordinator = RemediationCoordinator()

    result = coordinator.execute(
        action,
        expected="EXPECTED",
        observed="EXPECTED",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result is not None