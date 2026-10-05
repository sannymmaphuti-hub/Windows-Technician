# ==========================================
# Windows Technician v0.8
# REMOTE OPERATION STATE PERSISTENCE TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_remote_action(handler=None):
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


def build_connected_context():
    machine = build_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


def test_operation_starts_not_executed():
    action, operation = build_remote_action()

    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_authorized_operation_can_execute():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_connection_loss_after_execution_does_not_erase_execution_state():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

    session.disconnect()

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_connection_loss_does_not_change_executed_action_to_failed():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert action.execution_status != "FAILED"
    assert operation.execution_status != "FAILED"


def test_action_identity_survives_connection_loss():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action_id = action.action_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert action.action_id == action_id


def test_operation_identity_survives_connection_loss():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    operation_id = operation.operation_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert operation.operation_id == operation_id


def test_reconnection_does_not_create_new_action():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action_id = action.action_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    assert action.action_id == action_id


def test_reconnection_does_not_create_new_operation():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    operation_id = operation.operation_id

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    assert operation.operation_id == operation_id


def test_reconnection_preserves_executed_state():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_disconnected_machine_cannot_execute_new_remote_action():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_existing_executed_action_is_not_reexecuted_after_reconnection():
    machine, session, context = build_connected_context()

    execution_count = {"value": 0}

    def handler():
        execution_count["value"] += 1

    action, operation = build_remote_action(handler)

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert execution_count["value"] == 1

    session.disconnect()
    session.connect()

    assert executor.execute(action) is False
    assert execution_count["value"] == 1

    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"


def test_connection_loss_does_not_authorize_action():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    assert action.authorization_status == "UNAUTHORIZED"

    session.disconnect()

    assert action.authorization_status == "UNAUTHORIZED"


def test_connection_loss_does_not_create_retry():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert not hasattr(action, "retry")
    assert not hasattr(action, "retry_count")


def test_reconnection_does_not_create_recovery_workflow():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()
    session.connect()

    assert not hasattr(action, "recover")
    assert not hasattr(action, "reinvestigate")


def test_remote_execution_state_is_preserved_without_creating_duplicate_state_models():
    machine, session, context = build_connected_context()
    action, operation = build_remote_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    session.disconnect()

    assert hasattr(action, "execution_status")
    assert hasattr(operation, "execution_status")

    assert not hasattr(action, "remote_execution_status")
    assert not hasattr(action, "recovery_status")