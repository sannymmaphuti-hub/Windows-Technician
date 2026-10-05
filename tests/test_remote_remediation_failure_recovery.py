# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION FAILURE & RECOVERY TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remote_remediation_executor import (
    RemoteRemediationExecutor,
)
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier


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
    if handler is None:

        def handler():
            return None

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


def execute_remote_action(context, action):
    executor = RemoteRemediationExecutor(context)

    action.authorize()

    return executor.execute(action)


def test_execution_success_followed_by_failed_verification_is_recoverable():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_mark_action_as_execution_failure():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_trigger_blind_retry():
    calls = []

    def handler():
        calls.append(True)

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert calls == [True]
    assert action.execution_status == "EXECUTED"


def test_remote_session_can_disconnect_after_failed_verification():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False

    context.session.disconnect()

    assert context.session.state == "DISCONNECTED"
    assert machine.is_available is False


def test_disconnect_does_not_erase_failed_verification_history():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    context.session.disconnect()

    assert result.action_id == action.action_id
    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_disconnected_machine_cannot_be_blindly_retried():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False

    context.session.disconnect()

    executor = RemoteRemediationExecutor(context)

    retry_result = executor.execute(action)

    assert retry_result is False
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_reconnection_does_not_erase_previous_execution_state():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    context.session.disconnect()
    context.session.connect()

    assert machine.is_available is True
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is False


def test_reconnection_does_not_create_new_action():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    original_action_id = action.action_id

    context.session.disconnect()
    context.session.connect()

    assert action.action_id == original_action_id
    assert action.operation is operation


def test_recovery_must_use_existing_action_history():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"
    assert action.authorization_status == "AUTHORIZED"


def test_remote_context_does_not_create_recovery_workflow():
    machine = build_machine()
    context = build_context(machine)

    assert not hasattr(context, "recover")
    assert not hasattr(context, "retry")
    assert not hasattr(context, "reinvestigate")
    assert not hasattr(context, "create_recovery_workflow")


def test_remote_executor_does_not_create_recovery_workflow():
    machine = build_machine()
    context = build_context(machine)
    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "recover")
    assert not hasattr(executor, "retry")
    assert not hasattr(executor, "reinvestigate")


def test_verification_failure_is_distinct_from_remote_execution_failure():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status != "FAILED"


def test_remote_execution_failure_remains_distinct_from_verification_failure():
    def handler():
        raise RuntimeError("remote execution failed")

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    assert execute_remote_action(context, action) is False
    assert action.execution_status == "FAILED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True
    assert action.execution_status == "FAILED"


def test_remote_failure_preserves_machine_identity():
    machine = build_machine()
    context = build_context(machine)

    def handler():
        raise RuntimeError("remote execution failed")

    operation = build_operation(handler)
    action = build_action(operation)

    execute_remote_action(context, action)

    assert context.machine_id == "machine-001"
    assert context.hostname == "REMOTE-PC"
    assert context.session_id is not None


def test_remote_failure_preserves_action_identity():
    machine = build_machine()
    context = build_context(machine)

    def handler():
        raise RuntimeError("remote execution failed")

    operation = build_operation(handler)
    action = build_action(operation)

    execute_remote_action(context, action)

    assert action.action_id == "remote-action-001"
    assert action.category == "MEMORY"
    assert action.severity == "HIGH"


def test_recovery_does_not_silently_reauthorize_action():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    action.deny()

    context.session.disconnect()
    context.session.connect()

    assert action.authorization_status == "DENIED"

    executor = RemoteRemediationExecutor(context)

    result = executor.execute(action)

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_recovery_boundary_preserves_existing_remediation_contract():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert context.is_remote is True
    assert action.requires_authorization is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.operation is operation