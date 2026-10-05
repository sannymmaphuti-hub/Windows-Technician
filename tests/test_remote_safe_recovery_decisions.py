# ==========================================
# Windows Technician v0.8
# REMOTE SAFE RECOVERY DECISION TESTS
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


def execute_action(context, action):
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True


def verify_action(action, observed):
    verifier = RemediationVerifier()

    return verifier.verify(
        expected="COMPLETED",
        observed=observed,
        action_id=action.action_id,
    )


def test_verified_success_is_distinct_from_execution_success():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    assert action.execution_status == "EXECUTED"

    result = verify_action(action, "COMPLETED")

    assert result.verification_result["verified"] is True


def test_execution_success_without_verification_is_not_verified():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    assert action.execution_status == "EXECUTED"

    session.disconnect()

    assert action.execution_status == "EXECUTED"


def test_unknown_actual_state_is_not_success():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    result = verify_action(action, "UNKNOWN")

    assert result.verification_result["verified"] is False


def test_unknown_actual_state_is_not_execution_failure():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    result = verify_action(action, "UNKNOWN")

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_failed_actual_state_is_distinct_from_unknown():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    unknown_result = verify_action(action, "UNKNOWN")
    failed_result = verify_action(action, "FAILED")

    assert unknown_result.verification_result["verified"] is False
    assert failed_result.verification_result["verified"] is False

    assert (
        unknown_result.verification_result["observed"]
        != failed_result.verification_result["observed"]
    )


def test_failed_verification_does_not_change_execution_status():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    result = verify_action(action, "FAILED")

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_create_execution_failure():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert operation.execution_status == "EXECUTED"


def test_unknown_state_does_not_trigger_retry():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "UNKNOWN")

    assert not hasattr(action, "retry")
    assert not hasattr(action, "retry_count")


def test_failed_state_does_not_trigger_retry():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert not hasattr(action, "retry")
    assert not hasattr(action, "retry_count")


def test_reconnection_does_not_authorize_again():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    assert action.authorization_status == "AUTHORIZED"

    session.disconnect()
    session.connect()

    verify_action(action, "UNKNOWN")

    assert action.authorization_status == "AUTHORIZED"


def test_denied_action_remains_denied_after_connection_recovery():
    machine, session, context = build_context()
    action, operation = build_action()

    action.deny()

    session.disconnect()
    session.connect()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_remains_unauthorized_after_connection_recovery():
    machine, session, context = build_context()
    action, operation = build_action()

    session.disconnect()
    session.connect()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_recovery_does_not_create_new_action_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    original_action_id = action.action_id

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert action.action_id == original_action_id


def test_recovery_does_not_create_new_operation_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    original_operation_id = operation.operation_id

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert operation.operation_id == original_operation_id


def test_machine_identity_survives_recovery_decision():
    machine, session, context = build_context()
    action, operation = build_action()

    machine_id = machine.machine_id

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert machine.machine_id == machine_id


def test_session_identity_survives_recovery_decision():
    machine, session, context = build_context()
    action, operation = build_action()

    session_id = session.session_id

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert session.session_id == session_id


def test_remote_context_does_not_decide_recovery():
    machine, session, context = build_context()

    assert not hasattr(context, "recover")
    assert not hasattr(context, "retry")
    assert not hasattr(context, "decide_recovery")


def test_remote_executor_does_not_decide_recovery():
    machine, session, context = build_context()

    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "recover")
    assert not hasattr(executor, "retry")
    assert not hasattr(executor, "decide_recovery")


def test_verifier_only_reports_actual_verification_result():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    result = verify_action(action, "FAILED")

    assert result.verification_result["verified"] is False
    assert result.verification_result["expected"] == "COMPLETED"
    assert result.verification_result["observed"] == "FAILED"


def test_safe_recovery_boundary_preserves_existing_verifier():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="UNKNOWN",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert result.action_id == action.action_id


def test_safe_recovery_does_not_create_duplicate_recovery_system():
    machine, session, context = build_context()
    action, operation = build_action()

    execute_action(context, action)

    session.disconnect()
    session.connect()

    verify_action(action, "FAILED")

    assert not hasattr(action, "recovery_operation")
    assert not hasattr(action, "recovery_action")
    assert not hasattr(operation, "recovery_operation")