from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def create_remote_environment():
    machine = ManagedMachine(
        machine_id="machine-remote-remediation-001",
        hostname="REMOTE-REMEDIATION-PC",
        platform="Windows",
        operating_system="Windows 10",
    )

    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


def create_case(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    return case


def create_action():
    operation = RemediationOperation(
        operation_id="remote-memory-review-operation",
        description="Review remote memory pressure.",
        handler=lambda: None,
    )

    return RemediationAction(
        action_id="remote-memory-review",
        description="Review memory pressure on the remote machine.",
        requires_authorization=True,
        operation=operation,
        category="MEMORY",
        severity="HIGH",
    )


def authorize_action(action):
    action.authorize()
    return action


def prepare_workflow_for_remediation(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()


def prepare_workflow_for_verification(workflow):
    prepare_workflow_for_remediation(workflow)
    workflow.start_verification()


def test_remote_environment_is_connected():
    machine, session, context = create_remote_environment()

    assert machine.connection_state == "CONNECTED"
    assert session.state == "CONNECTED"
    assert context.is_remote is True


def test_remote_context_preserves_machine_identity():
    machine, session, context = create_remote_environment()

    assert context.machine_id == machine.machine_id
    assert context.hostname == machine.hostname


def test_remote_context_preserves_session_identity():
    machine, session, context = create_remote_environment()

    assert context.session_id == session.session_id


def test_remote_action_starts_unauthorized():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_action_requires_explicit_authorization():
    machine, session, context = create_remote_environment()
    action = create_action()
    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_action_can_be_authorized():
    action = create_action()

    authorize_action(action)

    assert action.authorization_status == "AUTHORIZED"


def test_remote_executor_executes_authorized_action():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_remote_operation_records_execution():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    assert action.operation.execution_status == "EXECUTED"


def test_remote_execution_does_not_equal_verification():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_status": "NORMAL"},
        observed={"memory_status": "WARNING"},
        action_id=action.action_id,
    )

    assert action.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is False


def test_remote_verification_contains_action_identity():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_status": "NORMAL"},
        observed={"memory_status": "WARNING"},
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["action_id"] == action.action_id


def test_remote_verification_failure_preserves_execution_state():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_status": "NORMAL"},
        observed={"memory_status": "WARNING"},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_remote_case_can_enter_workflow():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert workflow.state.value == "OPEN"


def test_remote_workflow_can_begin_investigation():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state.value == "INVESTIGATING"


def test_remote_workflow_can_progress_to_remediation():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    prepare_workflow_for_remediation(workflow)

    assert workflow.state.value == "REMEDIATING"


def test_remote_workflow_can_progress_to_verification():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    prepare_workflow_for_verification(workflow)

    assert workflow.state.value == "VERIFYING"


def test_remote_workflow_can_resolve_after_successful_verification():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    prepare_workflow_for_verification(workflow)
    workflow.resolve()

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal is True


def test_failed_remote_verification_does_not_mark_case_resolved():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    prepare_workflow_for_verification(workflow)

    verifier = RemediationVerifier()
    action = authorize_action(create_action())
    executor = RemoteRemediationExecutor(context)

    executor.execute(action)

    result = verifier.verify(
        expected={"memory_status": "NORMAL"},
        observed={"memory_status": "WARNING"},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert workflow.state.value == "VERIFYING"
    assert workflow.is_terminal is False


def test_failed_remote_verification_preserves_workflow_history():
    machine, session, context = create_remote_environment()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)

    prepare_workflow_for_verification(workflow)
    history_before = list(workflow.history)

    verifier = RemediationVerifier()
    action = authorize_action(create_action())
    executor = RemoteRemediationExecutor(context)

    executor.execute(action)

    verifier.verify(
        expected={"memory_status": "NORMAL"},
        observed={"memory_status": "WARNING"},
        action_id=action.action_id,
    )

    assert workflow.history == history_before


def test_remote_connection_loss_does_not_mark_action_failed_automatically():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_connection_recovery_allows_future_execution():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"

    session.connect()

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_remote_recovery_does_not_repeat_already_executed_action():
    machine, session, context = create_remote_environment()
    action = authorize_action(create_action())

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"

    session.disconnect()
    session.connect()

    assert executor.execute(action) is False
    assert action.execution_status == "EXECUTED"