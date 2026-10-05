# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION OPERATION BINDING TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation


def build_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    return RemoteRemediationContext(
        machine,
        session,
    )


def build_operation(handler=None):
    return RemediationOperation(
        operation_id="memory_review",
        description="Review memory pressure",
        handler=handler,
    )


def build_action(operation=None):
    return RemediationAction(
        action_id="remote-action-001",
        description="Review high memory usage",
        category="MEMORY",
        severity="HIGH",
        operation=operation,
    )


def test_remote_action_can_hold_existing_remediation_operation():
    operation = build_operation()
    action = build_action(operation)

    assert action.operation is operation


def test_remote_action_does_not_create_a_second_operation():
    operation = build_operation()
    action = build_action(operation)

    assert action.operation is operation
    assert isinstance(action.operation, RemediationOperation)


def test_remote_context_is_independent_of_operation_binding():
    context = build_context()
    operation = build_operation()
    action = build_action(operation)

    assert context.is_remote is True
    assert action.operation is operation


def test_remote_action_starts_unauthorized_even_with_operation_bound():
    operation = build_operation()
    action = build_action(operation)

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_bound_operation_does_not_execute_automatically():
    executed = []

    def handler():
        executed.append(True)

    operation = build_operation(handler)
    action = build_action(operation)

    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_unauthorized_remote_action_cannot_execute_bound_operation():
    executed = []

    def handler():
        executed.append(True)

    operation = build_operation(handler)
    action = build_action(operation)

    result = action.execute()

    assert result is False
    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_authorized_remote_action_executes_bound_operation():
    executed = []

    def handler():
        executed.append(True)

    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    result = action.execute()

    assert result is True
    assert executed == [True]
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_remote_context_does_not_bypass_action_authorization():
    context = build_context()
    operation = build_operation()
    action = build_action(operation)

    assert context.is_remote is True
    assert action.authorization_status == "UNAUTHORIZED"

    result = action.execute()

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_operation_failure_is_recorded_on_remote_action():
    def handler():
        raise RuntimeError("remote operation failed")

    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    result = action.execute()

    assert result is False
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"
    assert action.failure_reason == "remote operation failed"


def test_failed_remote_operation_cannot_execute_again():
    calls = []

    def handler():
        calls.append(True)
        raise RuntimeError("remote operation failed")

    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    first_result = action.execute()
    second_result = action.execute()

    assert first_result is False
    assert second_result is False
    assert calls == [True]
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"


def test_remote_identity_remains_available_while_operation_is_bound():
    context = build_context()
    operation = build_operation()
    action = build_action(operation)

    assert context.machine_id == "machine-001"
    assert context.hostname == "REMOTE-PC"
    assert context.session_id is not None
    assert action.operation is operation


def test_remote_operation_binding_preserves_existing_remediation_contract():
    context = build_context()
    operation = build_operation()
    action = build_action(operation)

    assert context.is_remote is True
    assert action.requires_authorization is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.operation is operation