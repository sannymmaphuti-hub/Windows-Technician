# ==========================================
# Windows Technician v0.8
# REMOTE CONNECTION RECOVERY TESTS
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


def test_disconnect_makes_machine_unavailable():
    machine, session, context = build_context()

    assert machine.is_available is True

    session.disconnect()

    assert machine.is_available is False


def test_reconnect_restores_machine_availability():
    machine, session, context = build_context()

    session.disconnect()

    assert machine.is_available is False

    session.connect()

    assert machine.is_available is True


def test_reconnect_restores_connected_session_state():
    machine, session, context = build_context()

    session.disconnect()
    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


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


def test_reconnect_does_not_authorize_existing_action():
    machine, session, context = build_context()
    action, operation = build_action()

    assert action.authorization_status == "UNAUTHORIZED"

    session.disconnect()
    session.connect()

    assert action.authorization_status == "UNAUTHORIZED"


def test_reconnect_does_not_execute_existing_action():
    machine, session, context = build_context()
    action, operation = build_action()

    session.disconnect()
    session.connect()

    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_reconnect_does_not_create_new_action():
    machine, session, context = build_context()
    action, operation = build_action()

    action_id = action.action_id

    session.disconnect()
    session.connect()

    assert action.action_id == action_id


def test_reconnect_does_not_create_new_operation():
    machine, session, context = build_context()
    action, operation = build_action()

    operation_id = operation.operation_id

    session.disconnect()
    session.connect()

    assert operation.operation_id == operation_id


def test_executed_action_remains_executed_after_reconnect():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

    session.disconnect()
    session.connect()

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_reconnect_does_not_repeat_execution():
    machine, session, context = build_context()

    execution_count = {"value": 0}

    def handler():
        execution_count["value"] += 1

    action, operation = build_action(handler)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert execution_count["value"] == 1

    session.disconnect()
    session.connect()

    assert execution_count["value"] == 1


def test_reconnect_allows_existing_action_to_be_verified():
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


def test_failed_verification_remains_failed_after_reconnect():
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


def test_reconnect_does_not_trigger_retry_after_failed_verification():
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
    assert not hasattr(action, "retry")
    assert not hasattr(action, "retry_count")


def test_reconnect_does_not_create_recovery_workflow():
    machine, session, context = build_context()

    session.disconnect()
    session.connect()

    assert not hasattr(session, "recover")
    assert not hasattr(session, "retry")
    assert not hasattr(session, "reinvestigate")


def test_reconnect_preserves_machine_health_state():
    machine, session, context = build_context()

    machine.health_state = "UNHEALTHY"

    session.disconnect()
    session.connect()

    assert machine.health_state == "UNHEALTHY"


def test_reconnect_preserves_action_authorization_and_execution_state():
    machine, session, context = build_context()
    action, operation = build_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    authorization_status = action.authorization_status
    execution_status = action.execution_status

    session.disconnect()
    session.connect()

    assert action.authorization_status == authorization_status
    assert action.execution_status == execution_status


def test_reconnect_is_safe_without_an_existing_action():
    machine, session, context = build_context()

    session.disconnect()
    session.connect()

    assert machine.is_available is True
    assert session.state == "CONNECTED"


def test_reconnect_does_not_bypass_remote_executor_boundary():
    machine, session, context = build_context()

    assert not hasattr(session, "execute")
    assert not hasattr(session, "execute_action")
    assert not hasattr(context, "execute")
    assert not hasattr(context, "execute_action")