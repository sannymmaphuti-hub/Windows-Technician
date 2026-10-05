# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION EXECUTION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remote_remediation_executor import (
    RemoteRemediationExecutor,
)


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_context(machine):
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


def test_connected_remote_machine_can_execute_authorized_action():
    executed = []

    def handler():
        executed.append(True)

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    result = action.execute()

    assert context.is_remote is True
    assert machine.is_available is True
    assert result is True
    assert executed == [True]
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_remote_action_requires_authorization_before_execution():
    executed = []

    def handler():
        executed.append(True)

    machine = build_machine()
    build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    result = action.execute()

    assert result is False
    assert executed == []
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_remote_action_does_not_execute_automatically_when_connected():
    executed = []

    def handler():
        executed.append(True)

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    assert context.is_remote is True
    assert machine.is_available is True
    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_disconnected_remote_machine_cannot_execute_action():
    executed = []

    def handler():
        executed.append(True)

    machine = build_machine()
    context = build_context(machine)
    context.session.disconnect()

    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    result = executor.execute(action)

    assert machine.is_available is False
    assert result is False
    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_disconnect_before_execution_does_not_remove_authorization():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    action.authorize()
    context.session.disconnect()

    assert action.authorization_status == "AUTHORIZED"
    assert machine.is_available is False


def test_remote_execution_failure_is_recorded():
    def handler():
        raise RuntimeError("remote execution failed")

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    result = action.execute()

    assert context.is_remote is True
    assert result is False
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"
    assert action.failure_reason == "remote execution failed"


def test_failed_remote_action_is_not_executed_again():
    calls = []

    def handler():
        calls.append(True)
        raise RuntimeError("remote execution failed")

    machine = build_machine()
    build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    first_result = action.execute()
    second_result = action.execute()

    assert first_result is False
    assert second_result is False
    assert calls == [True]
    assert action.execution_status == "FAILED"


def test_successful_remote_action_is_not_executed_again():
    calls = []

    def handler():
        calls.append(True)

    machine = build_machine()
    build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    action.authorize()

    first_result = action.execute()
    second_result = action.execute()

    assert first_result is True
    assert second_result is False
    assert calls == [True]
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_remote_execution_preserves_machine_identity():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    action.authorize()
    action.execute()

    assert context.machine_id == "machine-001"
    assert context.hostname == "REMOTE-PC"
    assert context.session_id is not None


def test_remote_execution_preserves_action_identity():
    machine = build_machine()
    build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    action.authorize()
    action.execute()

    assert action.action_id == "remote-action-001"
    assert action.category == "MEMORY"
    assert action.severity == "HIGH"


def test_remote_context_does_not_execute_the_action_directly():
    machine = build_machine()
    context = build_context(machine)

    assert not hasattr(context, "execute")
    assert not hasattr(context, "execute_action")
    assert not hasattr(context, "execute_remediation")


def test_remote_execution_uses_existing_remediation_action_contract():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert context.is_remote is True
    assert action.requires_authorization is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.operation is operation