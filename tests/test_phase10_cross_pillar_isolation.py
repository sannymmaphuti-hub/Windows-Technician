import pytest

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
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_machine(machine_id="machine-1"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_connected_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def make_remote_diagnostic_input(machine, session):
    context = RemoteDiagnosticContext(machine, session)

    observation = Observation(
        source="system",
        subject="network",
        attribute="status",
        value="warning",
    )

    return RemoteDiagnosticInput(
        context=context,
        observations=[observation],
    )


def make_action(action_id="action-1", handler=None):
    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Test remediation operation",
        handler=handler or (lambda: None),
    )

    return RemediationAction(
        action_id=action_id,
        description="Test remediation action",
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


def make_proactive_case(machine):
    recommendation = make_proactive_recommendation(machine)
    return ProactiveCaseCreator().create(recommendation)


def prepare_investigating_workflow(case):
    workflow = TechnicianWorkflow(case)
    workflow.start_investigation()
    return workflow


def prepare_action_required_workflow(case):
    workflow = TechnicianWorkflow(case)
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    return workflow


# ---------------------------------------------------------------------------
# Local / Remote isolation
# ---------------------------------------------------------------------------

def test_local_case_does_not_create_remote_session_state():
    case = DiagnosticCase()
    workflow = prepare_investigating_workflow(case)

    assert workflow.state is WorkflowState.INVESTIGATING
    assert not hasattr(case, "session_id")


def test_remote_session_does_not_change_local_workflow_state():
    case = DiagnosticCase()
    workflow = prepare_investigating_workflow(case)

    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert session.state == "CONNECTED"


def test_remote_context_requires_remote_session():
    machine = make_machine()

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(machine, object())


def test_remote_remediation_context_requires_remote_session():
    machine = make_machine()

    with pytest.raises(ValueError):
        RemoteRemediationContext(machine, object())


def test_remote_diagnostic_context_is_distinct_from_remediation_context():
    machine = make_machine()
    session = make_connected_session(machine)

    diagnostic_context = RemoteDiagnosticContext(machine, session)
    remediation_context = RemoteRemediationContext(machine, session)

    assert diagnostic_context is not remediation_context
    assert diagnostic_context.session_id == remediation_context.session_id
    assert diagnostic_context.machine_id == remediation_context.machine_id


# ---------------------------------------------------------------------------
# Remote / Proactive isolation
# ---------------------------------------------------------------------------

def test_remote_connection_does_not_authorize_proactive_recommendation():
    machine = make_machine()
    session = make_connected_session(machine)

    recommendation = make_proactive_recommendation(machine)
    action = make_action()

    assert session.state == "CONNECTED"
    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_alert_does_not_connect_remote_session():
    machine = make_machine()
    session = RemoteSession(machine)

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is unusually high.",
    )

    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"
    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "UNKNOWN"


def test_proactive_recommendation_does_not_change_remote_session():
    machine = make_machine()
    session = RemoteSession(machine)

    recommendation = make_proactive_recommendation(machine)
    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"
    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "UNKNOWN"


def test_proactive_case_creation_does_not_create_remote_session():
    machine = make_machine()

    case = make_proactive_case(machine)

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert not hasattr(case, "session_id")


def test_proactive_case_is_not_a_remote_diagnostic_input():
    machine = make_machine()
    case = make_proactive_case(machine)

    session = make_connected_session(machine)

    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context=case,
            observations=[],
        )

    assert session.state == "CONNECTED"


# ---------------------------------------------------------------------------
# Proactive / Local authorization isolation
# ---------------------------------------------------------------------------

def test_proactive_recommendation_does_not_authorize_local_action():
    machine = make_machine()
    case = make_proactive_case(machine)
    workflow = prepare_action_required_workflow(case)
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_case_workflow_does_not_authorize_action():
    machine = make_machine()
    case = make_proactive_case(machine)
    workflow = prepare_action_required_workflow(case)
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED

    assert action.execute() is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_workflow_state_does_not_authorize_action():
    case = DiagnosticCase()
    workflow = prepare_action_required_workflow(case)
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execute() is False


def test_remote_connection_does_not_authorize_local_action():
    machine = make_machine()
    session = make_connected_session(machine)
    action = make_action()

    assert session.state == "CONNECTED"
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execute() is False


# ---------------------------------------------------------------------------
# Cross-pillar state mutation protection
# ---------------------------------------------------------------------------

def test_local_workflow_transition_does_not_change_machine_connection_state():
    machine = make_machine()
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname

    workflow = TechnicianWorkflow(case)
    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED
    assert machine.connection_state == "UNKNOWN"


def test_local_workflow_does_not_disconnect_remote_session():
    machine = make_machine()
    session = make_connected_session(machine)

    case = DiagnosticCase()
    workflow = prepare_investigating_workflow(case)
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED
    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_session_disconnect_does_not_change_local_workflow_state():
    machine = make_machine()
    session = make_connected_session(machine)

    case = DiagnosticCase()
    workflow = prepare_investigating_workflow(case)

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_alert_lifecycle_does_not_change_local_workflow():
    machine = make_machine()
    case = make_proactive_case(machine)
    workflow = prepare_investigating_workflow(case)

    alert = case.proactive_alert
    alert.acknowledge()
    alert.resolve()

    assert alert.status == "RESOLVED"
    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_recommendation_lifecycle_does_not_change_workflow():
    machine = make_machine()
    case = make_proactive_case(machine)
    workflow = prepare_investigating_workflow(case)

    recommendation = case.proactive_recommendation
    recommendation.acknowledge()
    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert workflow.state is WorkflowState.INVESTIGATING


# ---------------------------------------------------------------------------
# Machine identity isolation
# ---------------------------------------------------------------------------

def test_remote_context_cannot_cross_machine_identity():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(machine_b, session_a)


def test_remote_remediation_context_cannot_cross_machine_identity():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteRemediationContext(machine_b, session_a)


def test_proactive_alert_preserves_its_machine_identity():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    alert = ProactiveAlert(
        machine=machine_a,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    assert alert.machine_id == machine_a.machine_id
    assert alert.machine_id != machine_b.machine_id


def test_proactive_case_preserves_source_machine_identity():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    case = make_proactive_case(machine_a)

    assert case.machine_id == machine_a.machine_id
    assert case.hostname == machine_a.hostname
    assert case.machine_id != machine_b.machine_id


def test_two_proactive_cases_remain_machine_isolated():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    case_a = make_proactive_case(machine_a)
    case_b = make_proactive_case(machine_b)

    assert case_a.machine_id == machine_a.machine_id
    assert case_b.machine_id == machine_b.machine_id
    assert case_a.machine_id != case_b.machine_id


# ---------------------------------------------------------------------------
# Independent workflow isolation
# ---------------------------------------------------------------------------

def test_workflows_for_different_cases_are_independent():
    case_a = DiagnosticCase()
    case_b = DiagnosticCase()

    workflow_a = TechnicianWorkflow(case_a)
    workflow_b = TechnicianWorkflow(case_b)

    workflow_a.start_investigation()

    assert workflow_a.state is WorkflowState.INVESTIGATING
    assert workflow_b.state is WorkflowState.OPEN


def test_resolving_one_workflow_does_not_resolve_another():
    case_a = DiagnosticCase()
    case_b = DiagnosticCase()

    workflow_a = TechnicianWorkflow(case_a)
    workflow_b = TechnicianWorkflow(case_b)

    workflow_a.start_investigation()
    workflow_a.mark_diagnosed()
    workflow_a.require_action()
    workflow_a.start_remediation()
    workflow_a.start_verification()
    workflow_a.resolve()

    assert workflow_a.state is WorkflowState.RESOLVED
    assert workflow_b.state is WorkflowState.OPEN


def test_remote_session_state_is_independent_between_machines():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)
    session_b = RemoteSession(machine_b)

    assert session_a.state == "CONNECTED"
    assert session_b.state == "DISCONNECTED"
    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"


# ---------------------------------------------------------------------------
# Remote execution remains explicit
# ---------------------------------------------------------------------------

def test_remote_executor_does_not_execute_unauthorized_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_requires_its_own_correct_context():
    machine = make_machine()
    session = make_connected_session(machine)

    action = make_action()

    diagnostic_context = RemoteDiagnosticContext(machine, session)

    with pytest.raises(ValueError):
        RemoteRemediationExecutor(diagnostic_context)


def test_remote_executor_does_not_use_proactive_recommendation_as_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    recommendation = make_proactive_recommendation(machine)
    executor = RemoteRemediationExecutor(context)

    with pytest.raises(ValueError):
        executor.execute(recommendation)


def test_remote_executor_does_not_use_case_as_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    case = make_proactive_case(machine)
    executor = RemoteRemediationExecutor(context)

    with pytest.raises(ValueError):
        executor.execute(case)


# ---------------------------------------------------------------------------
# Remote diagnostic identity preservation
# ---------------------------------------------------------------------------

def test_remote_diagnostic_input_preserves_machine_identity():
    machine = make_machine()
    session = make_connected_session(machine)

    remote_input = make_remote_diagnostic_input(machine, session)

    assert remote_input.machine_id == machine.machine_id
    assert remote_input.session_id == session.session_id
    assert remote_input.is_remote is True


def test_remote_diagnostic_result_preserves_machine_identity():
    machine = make_machine()
    session = make_connected_session(machine)

    remote_input = make_remote_diagnostic_input(machine, session)
    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    assert result["machine_id"] == machine.machine_id
    assert result["hostname"] == machine.hostname
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True


def test_remote_diagnostic_does_not_authorize_an_action():
    machine = make_machine()
    session = make_connected_session(machine)

    remote_input = make_remote_diagnostic_input(machine, session)
    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    action = make_action()

    assert result["machine_id"] == machine.machine_id
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ---------------------------------------------------------------------------
# Connection-loss cross-pillar isolation
# ---------------------------------------------------------------------------

def test_remote_connection_loss_does_not_change_proactive_alert():
    machine = make_machine()
    session = make_connected_session(machine)

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"
    assert alert.status == "ACTIVE"


def test_remote_connection_loss_does_not_change_proactive_recommendation():
    machine = make_machine()
    session = make_connected_session(machine)

    recommendation = make_proactive_recommendation(machine)

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert recommendation.status == "PENDING"


def test_remote_connection_loss_does_not_change_local_workflow():
    machine = make_machine()
    session = make_connected_session(machine)

    case = DiagnosticCase()
    workflow = prepare_investigating_workflow(case)

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert workflow.state is WorkflowState.INVESTIGATING


def test_remote_connection_loss_does_not_execute_pending_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    session.disconnect()

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


# ---------------------------------------------------------------------------
# Final cross-pillar invariants
# ---------------------------------------------------------------------------

def test_detection_does_not_become_authorization():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is unusually high.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate CPU usage.",
    )

    action = make_action()

    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_remote_connection_does_not_become_authorization():
    machine = make_machine()
    session = make_connected_session(machine)
    action = make_action()

    assert session.state == "CONNECTED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_case_creation_does_not_become_authorization():
    machine = make_machine()
    case = make_proactive_case(machine)
    action = make_action()

    assert case.machine_id == machine.machine_id
    assert action.authorization_status == "UNAUTHORIZED"


def test_workflow_progression_does_not_become_authorization():
    case = DiagnosticCase()
    workflow = prepare_action_required_workflow(case)
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"


def test_all_three_pillars_keep_remediation_explicit():
    machine = make_machine()
    session = make_connected_session(machine)

    proactive_case = make_proactive_case(machine)
    proactive_workflow = prepare_action_required_workflow(proactive_case)

    local_case = DiagnosticCase()
    local_workflow = prepare_action_required_workflow(local_case)

    remote_context = RemoteRemediationContext(machine, session)

    proactive_action = make_action("proactive-action")
    local_action = make_action("local-action")
    remote_action = make_action("remote-action")

    assert proactive_workflow.state is WorkflowState.ACTION_REQUIRED
    assert local_workflow.state is WorkflowState.ACTION_REQUIRED
    assert remote_context.is_remote is True

    assert proactive_action.authorization_status == "UNAUTHORIZED"
    assert local_action.authorization_status == "UNAUTHORIZED"
    assert remote_action.authorization_status == "UNAUTHORIZED"

    assert proactive_action.execute() is False
    assert local_action.execute() is False
    assert RemoteRemediationExecutor(remote_context).execute(remote_action) is False

    assert proactive_action.execution_status == "NOT_EXECUTED"
    assert local_action.execution_status == "NOT_EXECUTED"
    assert remote_action.execution_status == "NOT_EXECUTED"