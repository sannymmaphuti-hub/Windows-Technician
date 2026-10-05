from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.technician_workspace import TechnicianWorkspace
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor


def make_machine(machine_id="machine-1"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def make_operation(operation_id="operation-1"):
    return RemediationOperation(
        operation_id=operation_id,
        description="Test operation",
        handler=lambda: None,
    )


def make_action(action_id="action-1"):
    return RemediationAction(
        action_id=action_id,
        description="Test remediation",
        operation=make_operation(),
    )


def test_managed_machine_starts_unknown():
    machine = make_machine()

    assert machine.connection_state == "UNKNOWN"
    assert machine.health_state == "UNKNOWN"
    assert machine.last_seen is None


def test_managed_machine_identity_is_preserved():
    machine = make_machine("abc")

    assert machine.machine_id == "abc"
    assert machine.hostname == "HOST-abc"


def test_remote_session_updates_machine_connection_state():
    machine = make_machine()
    session = RemoteSession(machine)

    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True


def test_remote_session_disconnect_updates_machine():
    machine = make_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"
    assert machine.is_available is False


def test_remote_context_preserves_machine_identity():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(machine, session)

    assert context.machine_id == machine.machine_id
    assert context.hostname == machine.hostname
    assert context.session_id == session.session_id
    assert context.is_remote is True


def test_remote_input_preserves_identity():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(machine, session)
    remote_input = RemoteDiagnosticInput(context, [])

    assert remote_input.machine_id == machine.machine_id
    assert remote_input.session_id == session.session_id
    assert remote_input.is_remote is True
    assert remote_input.context.hostname == machine.hostname


def test_remediation_requires_explicit_authorization():
    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_execute():
    action = make_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorized_action_executes():
    action = make_action()

    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"


def test_execution_is_not_verification():
    action = make_action()
    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()
    result = verifier.verify(
        expected={"healthy": True},
        observed={"healthy": False},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_resolve_workflow():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING

    verifier = RemediationVerifier()
    result = verifier.verify(
        expected={"healthy": True},
        observed={"healthy": False},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING


def test_resolved_workflow_requires_explicit_reopen():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_workflow_history_preserves_lifecycle():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert len(workflow.history) == 6
    assert workflow.history[0] == (
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
    )
    assert workflow.history[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
    )


def test_workspace_is_read_oriented():
    workflow = make_workflow()
    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is workflow.case
    assert workspace.case_id == workflow.case.case_id
    assert workspace.state is WorkflowState.OPEN


def test_proactive_recommendation_does_not_execute():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_PRESSURE",
        metric="memory_usage",
        message="Memory usage is elevated.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Review memory usage.",
    )

    assert recommendation.status == "PENDING"
    assert not hasattr(recommendation, "execute")


def test_proactive_case_creation_preserves_identity():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_PRESSURE",
        metric="memory_usage",
        message="Memory usage is elevated.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Review memory usage.",
    )

    case = ProactiveCaseCreator().create(recommendation)

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert case.proactive_alert is alert
    assert case.proactive_recommendation is recommendation


def test_proactive_case_creation_does_not_create_remediation():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_PRESSURE",
        metric="cpu_usage",
        message="CPU usage is elevated.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate CPU usage.",
    )

    case = ProactiveCaseCreator().create(recommendation)

    assert not hasattr(case, "remediation_action")


def test_remote_remediation_context_requires_matching_machine():
    machine = make_machine()
    other_machine = make_machine("machine-2")

    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)

    assert context.machine_id == machine.machine_id

    try:
        RemoteRemediationContext(other_machine, session)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Remote remediation context accepted a mismatched machine."
        )


def test_remote_remediation_requires_available_machine():
    machine = make_machine()
    session = RemoteSession(machine)

    try:
        RemoteRemediationContext(machine, session)
    except ValueError as error:
        assert str(error) == (
            "Remote remediation requires an available machine."
        )
    else:
        raise AssertionError(
            "Remote remediation context accepted an unavailable machine."
        )

def test_remote_remediation_requires_authorization():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_remediation_executes_after_authorization():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_connection_loss_does_not_rewrite_action_state():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"

    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "EXECUTED"


def test_executed_action_is_not_repeated():
    calls = []

    operation = RemediationOperation(
        operation_id="operation-1",
        description="Tracked operation",
        handler=lambda: calls.append("executed"),
    )

    action = RemediationAction(
        action_id="action-1",
        description="Tracked remediation",
        operation=operation,
    )

    action.authorize()

    assert action.execute() is True
    assert calls == ["executed"]

    assert action.execute() is False
    assert calls == ["executed"]


def test_multiple_machines_keep_connection_state_isolated():
    machine_a = make_machine("a")
    machine_b = make_machine("b")

    session_a = RemoteSession(machine_a)
    session_b = RemoteSession(machine_b)

    session_a.connect()

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"

    session_b.connect()

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"

    session_a.disconnect()

    assert machine_a.connection_state == "DISCONNECTED"
    assert machine_b.connection_state == "CONNECTED"


def test_multiple_actions_keep_execution_state_isolated():
    action_a = make_action("action-a")
    action_b = make_action("action-b")

    action_a.authorize()
    action_a.execute()

    assert action_a.execution_status == "EXECUTED"
    assert action_b.execution_status == "NOT_EXECUTED"


def test_multiple_workflows_keep_state_isolated():
    workflow_a = make_workflow()
    workflow_b = make_workflow()

    workflow_a.start_investigation()

    assert workflow_a.state is WorkflowState.INVESTIGATING
    assert workflow_b.state is WorkflowState.OPEN


def test_complete_local_lifecycle():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_complete_remote_lifecycle():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(machine, session)
    remote_input = RemoteDiagnosticInput(context, [])

    workflow = TechnicianWorkflow(DiagnosticCase())

    assert remote_input.machine_id == machine.machine_id
    assert remote_input.context.hostname == machine.hostname
    assert remote_input.session_id == session.session_id

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED

def test_complete_proactive_lifecycle():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_PRESSURE",
        metric="memory_usage",
        message="Memory usage is elevated.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate memory usage.",
    )

    case = ProactiveCaseCreator().create(recommendation)
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert workflow.case.machine_id == machine.machine_id