# ==========================================
# Windows Technician v0.8
# REMOTE RELIABILITY BOUNDARY TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier


def build_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


def build_action(handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id="operation-001",
        description="Test remote operation",
        handler=handler,
    )

    action = RemediationAction(
        action_id="action-001",
        description="Test remote remediation",
        requires_authorization=True,
        operation=operation,
        category="TEST",
        severity="HIGH",
    )

    return action, operation


def test_disconnected_machine_cannot_execute():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()
    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_connecting_machine_cannot_execute():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    session.state = "CONNECTING"
    machine.connection_state = "CONNECTING"

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_failed_connection_cannot_execute():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_cannot_execute_when_connected():
    machine, session, context = build_context()
    action, operation = build_action()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_denied_action_cannot_execute_when_connected():
    machine, session, context = build_context()
    action, operation = build_action()

    action.deny()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_reconnection_does_not_auto_execute():
    machine, session, context = build_context()

    execution_count = {"value": 0}

    def handler():
        execution_count["value"] += 1

    action, operation = build_action(handler)

    action.authorize()

    session.disconnect()
    session.connect()

    assert execution_count["value"] == 0
    assert action.execution_status == "NOT_EXECUTED"


def test_reconnection_does_not_auto_authorize():
    machine, session, context = build_context()
    action, operation = build_action()

    session.disconnect()
    session.connect()

    assert action.authorization_status == "UNAUTHORIZED"


def test_connection_loss_does_not_change_execution_to_failed():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    assert executor.execute(action) is True

    session.disconnect()

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_connection_loss_does_not_change_execution_to_unknown():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    assert executor.execute(action) is True

    session.disconnect()

    assert action.execution_status != "UNKNOWN"
    assert operation.execution_status != "UNKNOWN"


def test_unknown_verification_does_not_change_execution_status():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="UNKNOWN",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_failed_verification_does_not_change_execution_status():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="FAILED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_verification_cannot_execute_action():
    machine, session, context = build_context()
    action, operation = build_action()

    verifier = RemediationVerifier()

    verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert action.execution_status == "NOT_EXECUTED"


def test_verification_cannot_authorize_action():
    machine, session, context = build_context()
    action, operation = build_action()

    verifier = RemediationVerifier()

    verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert action.authorization_status == "UNAUTHORIZED"


def test_executor_does_not_verify_action():
    machine, session, context = build_context()
    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "verify")
    assert not hasattr(executor, "verify_action")


def test_executor_does_not_authorize_action():
    machine, session, context = build_context()
    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "authorize")
    assert not hasattr(executor, "approve")


def test_executor_does_not_retry_action():
    machine, session, context = build_context()
    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "retry")
    assert not hasattr(executor, "retry_action")


def test_session_does_not_execute_remediation():
    machine, session, context = build_context()

    assert not hasattr(session, "execute")
    assert not hasattr(session, "execute_action")
    assert not hasattr(session, "remediate")


def test_session_does_not_verify_remediation():
    machine, session, context = build_context()

    assert not hasattr(session, "verify")
    assert not hasattr(session, "verify_action")


def test_context_does_not_execute_remediation():
    machine, session, context = build_context()

    assert not hasattr(context, "execute")
    assert not hasattr(context, "execute_action")
    assert not hasattr(context, "remediate")


def test_context_does_not_verify_remediation():
    machine, session, context = build_context()

    assert not hasattr(context, "verify")
    assert not hasattr(context, "verify_action")


def test_reconnect_preserves_action_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    action_id = action.action_id

    session.disconnect()
    session.connect()

    assert action.action_id == action_id


def test_reconnect_preserves_operation_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    operation_id = operation.operation_id

    session.disconnect()
    session.connect()

    assert operation.operation_id == operation_id


def test_reconnect_preserves_machine_identity():
    machine, session, context = build_context()

    machine_id = machine.machine_id

    session.disconnect()
    session.connect()

    assert machine.machine_id == machine_id


def test_reconnect_preserves_session_identity():
    machine, session, context = build_context()

    session_id = session.session_id

    session.disconnect()
    session.connect()

    assert session.session_id == session_id


def test_reliability_does_not_create_duplicate_action_state():
    machine, session, context = build_context()
    action, operation = build_action()

    assert not hasattr(action, "remote_execution_status")
    assert not hasattr(action, "recovery_status")
    assert not hasattr(action, "connection_status")


def test_reliability_does_not_create_duplicate_operation_state():
    machine, session, context = build_context()
    action, operation = build_action()

    assert not hasattr(operation, "remote_execution_status")
    assert not hasattr(operation, "recovery_status")


def test_reliability_does_not_create_duplicate_verification_state():
    machine, session, context = build_context()
    action, operation = build_action()

    assert not hasattr(action, "remote_verification")
    assert not hasattr(action, "verification_engine")


def test_reliability_does_not_create_duplicate_recovery_state():
    machine, session, context = build_context()

    assert not hasattr(context, "recovery_operation")
    assert not hasattr(context, "recovery_workflow")
    assert not hasattr(context, "recovery_engine")


def test_execution_failure_remains_distinct_from_connection_loss():
    machine, session, context = build_context()

    def failing_handler():
        raise RuntimeError("operation failed")

    action, operation = build_action(failing_handler)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"

    session.disconnect()

    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"


def test_connection_loss_does_not_erase_execution_failure():
    machine, session, context = build_context()

    def failing_handler():
        raise RuntimeError("operation failed")

    action, operation = build_action(failing_handler)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False

    session.disconnect()

    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"


def test_failed_execution_is_not_converted_to_success_by_reconnect():
    machine, session, context = build_context()

    def failing_handler():
        raise RuntimeError("operation failed")

    action, operation = build_action(failing_handler)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False

    session.disconnect()
    session.connect()

    assert action.execution_status == "FAILED"
    assert operation.execution_status == "FAILED"


def test_reliability_boundary_preserves_existing_remediation_contract():
    machine, session, context = build_context()
    action, operation = build_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_reliability_boundary_preserves_existing_verification_contract():
    machine, session, context = build_context()
    action, operation = build_action()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["verified"] is True


def test_reliability_boundary_requires_explicit_action_authorization():
    machine, session, context = build_context()
    action, operation = build_action()

    executor = RemoteRemediationExecutor(context)

    session.disconnect()
    session.connect()

    assert executor.execute(action) is False
    assert action.authorization_status == "UNAUTHORIZED"


def test_reliability_boundary_requires_connected_machine_for_execution():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"