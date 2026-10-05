from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.observation import Observation
from engine.proactive_alert import ProactiveAlert
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.proactive_recommendation import ProactiveRecommendation
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remote_session import RemoteSession
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier
from engine.technician_workspace import TechnicianWorkspace
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def make_machine(machine_id="machine-1"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def make_observation(
    subject="network",
    value="warning",
):
    return Observation(
        source="system",
        subject=subject,
        attribute="status",
        value=value,
    )


def make_remote_input(
    machine,
    session,
    subject="network",
    value="warning",
):
    return RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(
            machine,
            session,
        ),
        observations=[
            make_observation(
                subject,
                value,
            )
        ],
    )


def make_workflow(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname

    return TechnicianWorkflow(case)


def make_action(
    action_id="action-1",
    handler=None,
):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Regression boundary operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Regression boundary action",
        requires_authorization=True,
        operation=operation,
    )


def make_proactive_recommendation(machine):
    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    return ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate memory usage.",
    )


def complete_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_managed_machine_exposes_canonical_identity_contract():
    machine = make_machine("rc-machine")

    assert machine.machine_id == "rc-machine"
    assert machine.hostname == "HOST-rc-machine"
    assert machine.platform == "Windows"
    assert machine.operating_system == "Windows 11"
    assert machine.connection_state == "UNKNOWN"
    assert machine.health_state == "UNKNOWN"
    assert machine.is_available is False


def test_remote_session_updates_only_canonical_machine_connection_state():
    machine = make_machine()

    session = make_session(machine)

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"
    assert machine.is_available is False


def test_remote_diagnostic_input_preserves_canonical_remote_identity():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(
        machine,
        session,
    )

    assert remote_input.machine_id == machine.machine_id
    assert remote_input.session_id == session.session_id
    assert remote_input.is_remote is True
    assert remote_input.context.machine is machine
    assert remote_input.context.session is session


def test_remote_diagnostic_pipeline_uses_diagnose_contract():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(
        machine,
        session,
    )

    pipeline = RemoteDiagnosticPipeline()

    result = pipeline.diagnose(remote_input)

    assert result["machine_id"] == machine.machine_id
    assert result["hostname"] == machine.hostname
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True


def test_remote_diagnostic_pipeline_does_not_execute_remediation():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(
        machine,
        session,
    )

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert "remediation_actions" not in result

    assert machine.connection_state == "CONNECTED"
    assert session.state == "CONNECTED"


def test_remediation_action_requires_explicit_authorization():
    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is False

    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_execute_action():
    execution_count = 0

    def handler():
        nonlocal execution_count
        execution_count += 1

    action = make_action(
        "authorization-only",
        handler,
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert execution_count == 0


def test_execution_requires_authorization_and_operation():
    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is False

    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"


def test_successful_execution_is_not_verification():
    action = make_action()

    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_change_execution_status():
    action = make_action()

    action.authorize()
    action.execute()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_verification_does_not_resolve_workflow():
    machine = make_machine()
    workflow = make_workflow(machine)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="verification-boundary",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING


def test_workflow_terminal_state_requires_explicit_resolution():
    machine = make_machine()
    workflow = make_workflow(machine)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING
    assert workflow.is_terminal is False

    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_resolved_workflow_requires_explicit_reopen():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False


def test_workflow_history_preserves_lifecycle():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow(workflow)

    expected = [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        ),
        (
            WorkflowState.INVESTIGATING,
            WorkflowState.DIAGNOSED,
        ),
        (
            WorkflowState.DIAGNOSED,
            WorkflowState.ACTION_REQUIRED,
        ),
        (
            WorkflowState.ACTION_REQUIRED,
            WorkflowState.REMEDIATING,
        ),
        (
            WorkflowState.REMEDIATING,
            WorkflowState.VERIFYING,
        ),
        (
            WorkflowState.VERIFYING,
            WorkflowState.RESOLVED,
        ),
    ]

    assert workflow.history == expected


def test_technician_workspace_is_read_oriented():
    machine = make_machine()
    workflow = make_workflow(machine)

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is workflow.case
    assert workspace.case_id == workflow.case.case_id
    assert workspace.machine_id == machine.machine_id
    assert workspace.hostname == machine.hostname
    assert workspace.state is WorkflowState.OPEN


def test_proactive_detection_creates_recommendation_not_execution():
    machine = make_machine()

    recommendation = make_proactive_recommendation(
        machine
    )

    assert recommendation.machine_id == machine.machine_id
    assert recommendation.status == "PENDING"
    assert recommendation.recommendation == (
        "Investigate memory usage."
    )


def test_proactive_case_creation_preserves_safety_boundary():
    machine = make_machine()

    recommendation = make_proactive_recommendation(
        machine
    )

    case = ProactiveCaseCreator().create(
        recommendation
    )

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert case.proactive_recommendation is recommendation
    assert case.proactive_alert is recommendation.alert


def test_proactive_case_creation_does_not_execute_remediation():
    machine = make_machine()

    recommendation = make_proactive_recommendation(
        machine
    )

    case = ProactiveCaseCreator().create(
        recommendation
    )

    assert not hasattr(
        case,
        "remediation_action",
    )

    assert recommendation.status == "PENDING"


def test_remote_remediation_requires_matching_machine_context():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    try:
        RemoteRemediationContext(
            machine_a,
            session_b,
        )
        assert False
    except ValueError:
        pass

    try:
        RemoteRemediationContext(
            machine_b,
            session_a,
        )
        assert False
    except ValueError:
        pass


def test_remote_remediation_requires_available_machine():
    machine = make_machine()
    session = make_session(machine)

    session.disconnect()

    try:
        RemoteRemediationContext(
            machine,
            session,
        )
        assert False
    except ValueError:
        pass


def test_remote_remediation_preserves_authorization_boundary():
    machine = make_machine()
    session = make_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(
        context
    )

    action = make_action(
        "remote-auth-boundary"
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_remediation_executes_only_after_authorization():
    machine = make_machine()
    session = make_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(
        context
    )

    action = make_action(
        "remote-authorized"
    )

    action.authorize()

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_connection_loss_is_not_automatically_operation_failure():
    machine = make_machine()
    session = make_session(machine)

    action = make_action(
        "connection-loss"
    )

    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"

    session.connect()

    assert machine.connection_state == "CONNECTED"
    assert action.execution_status == "NOT_EXECUTED"


def test_executed_action_is_not_repeated_after_reconnection():
    execution_count = 0

    def handler():
        nonlocal execution_count
        execution_count += 1

    machine = make_machine()
    session = make_session(machine)

    action = make_action(
        "no-repeat",
        handler,
    )

    action.authorize()

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(
        context
    )

    assert executor.execute(action) is True
    assert execution_count == 1

    session.disconnect()
    session.connect()

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(
        context
    )

    assert executor.execute(action) is False
    assert execution_count == 1


def test_case_workflow_remote_and_proactive_objects_share_machine_identity():
    machine = make_machine(
        "shared-identity"
    )

    session = make_session(machine)

    remote_input = make_remote_input(
        machine,
        session,
    )

    proactive_recommendation = (
        make_proactive_recommendation(machine)
    )

    proactive_case = ProactiveCaseCreator().create(
        proactive_recommendation
    )

    workflow = make_workflow(machine)

    assert remote_input.machine_id == machine.machine_id
    assert proactive_recommendation.machine_id == machine.machine_id
    assert proactive_case.machine_id == machine.machine_id
    assert workflow.case.machine_id == machine.machine_id


def test_multiple_cases_do_not_share_workflow_state():
    machine_a = make_machine("case-a")
    machine_b = make_machine("case-b")

    workflow_a = make_workflow(machine_a)
    workflow_b = make_workflow(machine_b)

    workflow_a.start_investigation()
    workflow_a.mark_diagnosed()

    assert workflow_a.state is WorkflowState.DIAGNOSED
    assert workflow_b.state is WorkflowState.OPEN

    assert workflow_a.history != workflow_b.history


def test_multiple_actions_do_not_share_execution_state():
    action_a = make_action("action-a")
    action_b = make_action("action-b")

    action_a.authorize()
    action_a.execute()

    assert action_a.execution_status == "EXECUTED"
    assert action_b.execution_status == "NOT_EXECUTED"

    assert action_a.operation.execution_status == "EXECUTED"
    assert action_b.operation.execution_status == "NOT_EXECUTED"


def test_multiple_machines_do_not_share_connection_state():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    session_a.disconnect()

    assert machine_a.connection_state == "DISCONNECTED"
    assert machine_b.connection_state == "CONNECTED"

    assert session_a.state == "DISCONNECTED"
    assert session_b.state == "CONNECTED"


def test_complete_local_workflow_remains_canonical():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True
    assert len(workflow.history) == 6


def test_complete_remote_lifecycle_remains_canonical():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(
        machine,
        session,
    )

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    workflow = TechnicianWorkflow(
        DiagnosticCase()
    )

    workflow.case.machine_id = result["machine_id"]
    workflow.case.hostname = result["hostname"]

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED
    assert workflow.case.machine_id == machine.machine_id


def test_complete_proactive_lifecycle_remains_canonical():
    machine = make_machine()

    recommendation = make_proactive_recommendation(
        machine
    )

    case = ProactiveCaseCreator().create(
        recommendation
    )

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED
    assert workflow.case is case
    assert workflow.case.machine_id == machine.machine_id