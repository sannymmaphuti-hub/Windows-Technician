# ==========================================
# Windows Technician v0.8
# REMOTE ACTUAL-STATE RECOVERY TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
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


def build_context():
    machine = build_machine()
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


def test_verifier_can_determine_actual_success_after_reconnection():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True
    assert result.verification_result["action_id"] == action.action_id


def test_verifier_can_determine_actual_failure_after_reconnection():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="FAILED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert result.verification_result["action_id"] == action.action_id


def test_verification_failure_does_not_change_execution_state_to_failed():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

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
    assert operation.execution_status == "EXECUTED"


def test_verification_is_linked_to_existing_action():
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
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["action_id"] == action.action_id


def test_reconnection_does_not_create_new_action_for_verification():
    machine, session, context = build_context()
    action, operation = build_action()

    original_action_id = action.action_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert action.action_id == original_action_id
    assert result.action_id == original_action_id


def test_reconnection_does_not_create_new_operation_for_verification():
    machine, session, context = build_context()
    action, operation = build_action()

    original_operation_id = operation.operation_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert operation.operation_id == original_operation_id


def test_connection_loss_does_not_count_as_verification_failure():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"

    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True


def test_actual_state_must_be_observed_after_reconnection():
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


def test_unknown_observed_state_does_not_become_success():
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


def test_unknown_observed_state_does_not_become_execution_failure():
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
    assert action.execution_status != "FAILED"
    assert operation.execution_status != "FAILED"


def test_verification_failure_does_not_trigger_retry():
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
    assert not hasattr(action, "retry")
    assert not hasattr(action, "retry_count")


def test_verification_does_not_reauthorize_action():
    machine, session, context = build_context()
    action, operation = build_action()

    assert action.authorization_status == "UNAUTHORIZED"

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True
    assert action.authorization_status == "UNAUTHORIZED"


def test_verification_preserves_machine_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    machine_id = machine.machine_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert machine.machine_id == machine_id


def test_verification_preserves_session_identity():
    machine, session, context = build_context()
    action, operation = build_action()

    session_id = session.session_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert session.session_id == session_id


def test_existing_verifier_remains_the_verification_authority():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    verifier = RemediationVerifier()

    assert hasattr(verifier, "verify")

    result = verifier.verify(
        expected="COMPLETED",
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True


def test_remote_context_does_not_perform_verification():
    machine, session, context = build_context()

    assert not hasattr(context, "verify")
    assert not hasattr(context, "verify_action")


def test_remote_executor_does_not_perform_verification():
    machine, session, context = build_context()

    executor = RemoteRemediationExecutor(context)

    assert not hasattr(executor, "verify")
    assert not hasattr(executor, "verify_action")


def test_actual_state_recovery_does_not_create_duplicate_verification_system():
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
        observed="COMPLETED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True
    assert not hasattr(action, "remote_verification")
    assert not hasattr(action, "recovery_verifier")