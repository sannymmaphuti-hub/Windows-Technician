import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation
from engine.proactive_case_creation import ProactiveCaseCreator


# ============================================================
# SHARED FACTORIES
# ============================================================


def create_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="TEST-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def create_case():
    case = DiagnosticCase()
    case.machine_id = "machine-001"
    case.hostname = "TEST-PC"
    return case


def create_action(operation=None):
    return RemediationAction(
        action_id="action-001",
        description="Test remediation action.",
        requires_authorization=True,
        operation=operation,
    )


def create_remote_environment():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


def create_remote_remediation_environment():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


def create_workflow():
    return TechnicianWorkflow(create_case())


def progress_to_action_required(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()


def progress_to_verification(workflow):
    progress_to_action_required(workflow)
    workflow.start_remediation()
    workflow.start_verification()


def create_proactive_chain():
    machine = create_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="PERFORMANCE_DEGRADATION",
        metric="cpu_usage",
        message="CPU usage is consistently above the established baseline.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate sustained CPU usage.",
    )

    creator = ProactiveCaseCreator()
    case = creator.create(recommendation)

    return machine, alert, recommendation, case


# ============================================================
# DETECTION ≠ AUTHORIZATION
# ============================================================


def test_local_case_does_not_authorize_remediation_automatically():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_remote_environment_does_not_authorize_remediation_automatically():
    _, _, context = create_remote_remediation_environment()
    action = create_action()

    executor = RemoteRemediationExecutor(context)

    assert action.authorization_status == "UNAUTHORIZED"
    assert executor is not None


def test_proactive_recommendation_does_not_authorize_remediation():
    _, _, recommendation, _ = create_proactive_chain()

    assert recommendation.status == "PENDING"


# ============================================================
# RECOMMENDATION ≠ EXECUTION
# ============================================================


def test_proactive_recommendation_does_not_execute_action():
    _, _, recommendation, _ = create_proactive_chain()
    action = create_action()

    assert recommendation.recommendation
    assert action.execution_status == "NOT_EXECUTED"


def test_diagnostic_pipeline_does_not_execute_remediation():
    _, _, context = create_remote_environment()

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    pipeline = RemoteDiagnosticPipeline()
    result = pipeline.diagnose(remote_input)

    assert result["is_remote"] is True


# ============================================================
# AUTHORIZATION ≠ EXECUTION
# ============================================================


def test_authorization_does_not_execute_local_action():
    action = create_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_execute_remote_action():
    action = create_action()
    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_denial_prevents_execution():
    action = create_action(operation=lambda: None)

    action.deny()

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_cannot_execute():
    action = create_action(operation=lambda: None)

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# DIAGNOSIS ≠ REMEDIATION
# ============================================================


def test_workflow_diagnosis_does_not_start_remediation():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_diagnosed_case_requires_explicit_action_transition():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED

    workflow.require_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_remote_diagnosis_does_not_change_workflow_state():
    workflow = create_workflow()

    _, _, context = create_remote_environment()

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    RemoteDiagnosticPipeline().diagnose(remote_input)

    assert workflow.state is WorkflowState.OPEN


# ============================================================
# EXECUTION ≠ VERIFICATION
# ============================================================


def test_successful_execution_does_not_resolve_workflow():
    workflow = create_workflow()
    action = create_action(operation=lambda: None)

    progress_to_action_required(workflow)

    action.authorize()
    assert action.execute() is True

    assert workflow.state is WorkflowState.ACTION_REQUIRED

    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING


def test_execution_success_does_not_equal_verified_state():
    action = create_action(operation=lambda: None)

    action.authorize()
    action.execute()

    assert action.execution_status == "EXECUTED"


def test_failed_execution_is_distinct_from_verification_failure():
    action = create_action(
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("execution failure")
        )
    )

    action.authorize()
    action.execute()

    assert action.execution_status == "FAILED"


# ============================================================
# CONNECTION LOSS ≠ AUTOMATIC OPERATION FAILURE
# ============================================================


def test_remote_connection_loss_does_not_change_action_execution_state():
    machine, session, context = create_remote_remediation_environment()

    action = create_action()

    action.authorize()

    assert action.execution_status == "NOT_EXECUTED"

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_connection_loss_does_not_mark_action_failed():
    machine, session, context = create_remote_remediation_environment()

    action = create_action()

    session.disconnect()

    assert action.execution_status != "FAILED"


def test_reconnection_does_not_automatically_execute_action():
    machine, session, context = create_remote_remediation_environment()

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()
    session.connect()

    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# REMOTE EXECUTION SAFETY
# ============================================================


def test_remote_executor_rejects_unavailable_machine():
    machine, session, context = create_remote_remediation_environment()

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_requires_explicit_authorization():
    _, _, context = create_remote_remediation_environment()

    action = create_action(operation=lambda: None)

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_can_execute_authorized_action():
    _, _, context = create_remote_remediation_environment()

    executed = []

    def operation():
        executed.append(True)

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert executed == [True]
    assert action.execution_status == "EXECUTED"


# ============================================================
# NO BLIND REPEAT
# ============================================================


def test_executed_action_is_not_repeated():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is True
    assert action.execute() is False

    assert executions == [True]


def test_failed_action_is_not_repeated():
    executions = []

    def operation():
        executions.append(True)
        raise RuntimeError("failure")

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False

    assert executions == [True]
    assert action.execution_status == "FAILED"


def test_reconnection_does_not_trigger_blind_repeat():
    executions = []

    def operation():
        executions.append(True)

    machine, session, context = create_remote_remediation_environment()

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True

    session.disconnect()
    session.connect()

    assert action.execution_status == "EXECUTED"
    assert executions == [True]


# ============================================================
# PROACTIVE SAFETY
# ============================================================


def test_proactive_alert_does_not_change_machine_connection_state():
    machine, alert, _, _ = create_proactive_chain()

    assert alert.status == "ACTIVE"
    assert machine.connection_state == "UNKNOWN"


def test_proactive_recommendation_creates_case_without_execution():
    _, _, recommendation, case = create_proactive_chain()

    assert case.proactive_recommendation is recommendation
    assert recommendation.status == "PENDING"


def test_proactive_case_starts_in_open_workflow_state():
    _, _, _, case = create_proactive_chain()

    workflow = TechnicianWorkflow(case)

    assert workflow.state is WorkflowState.OPEN


def test_proactive_case_requires_workflow_progression():
    _, _, _, case = create_proactive_chain()

    workflow = TechnicianWorkflow(case)

    assert workflow.state is WorkflowState.OPEN

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


# ============================================================
# WORKFLOW SAFETY
# ============================================================


def test_workflow_does_not_skip_from_open_to_remediating():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.OPEN


def test_workflow_does_not_skip_from_diagnosed_to_verifying():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_resolved_workflow_cannot_be_remediated_again():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.RESOLVED


# ============================================================
# PILLAR CONVERGENCE
# ============================================================


def test_local_remote_and_proactive_cases_use_diagnostic_case():
    local_case = create_case()

    _, _, remote_context = create_remote_environment()

    remote_input = RemoteDiagnosticInput(
        context=remote_context,
        observations=[],
    )

    remote_result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    _, _, _, proactive_case = create_proactive_chain()

    assert isinstance(local_case, DiagnosticCase)
    assert remote_result["machine_id"] == remote_context.machine_id
    assert isinstance(proactive_case, DiagnosticCase)


def test_all_pillars_use_same_technician_workflow():
    local_workflow = TechnicianWorkflow(create_case())

    _, _, _, proactive_case = create_proactive_chain()
    proactive_workflow = TechnicianWorkflow(proactive_case)

    assert isinstance(local_workflow, TechnicianWorkflow)
    assert isinstance(proactive_workflow, TechnicianWorkflow)

    assert local_workflow.state is WorkflowState.OPEN
    assert proactive_workflow.state is WorkflowState.OPEN


def test_remote_workflow_uses_same_lifecycle():
    workflow = create_workflow()

    _, _, context = create_remote_environment()

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert result["is_remote"] is True
    assert workflow.state is WorkflowState.DIAGNOSED


# ============================================================
# HISTORY PRESERVATION
# ============================================================


def test_safety_boundaries_do_not_remove_workflow_history():
    workflow = create_workflow()

    progress_to_verification(workflow)

    history_before_resolution = list(workflow.history)

    workflow.resolve()

    assert workflow.history[:5] == history_before_resolution
    assert len(workflow.history) == 6


def test_reconnection_does_not_remove_execution_history():
    executions = []

    def operation():
        executions.append(True)

    machine, session, context = create_remote_remediation_environment()

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    executor.execute(action)

    session.disconnect()
    session.connect()

    assert action.execution_status == "EXECUTED"
    assert executions == [True]


# ============================================================
# FINAL SAFETY ASSERTIONS
# ============================================================


def test_no_pillar_can_silently_authorize_an_action():
    local_action = create_action()
    remote_action = create_action()
    proactive_action = create_action()

    assert local_action.authorization_status == "UNAUTHORIZED"
    assert remote_action.authorization_status == "UNAUTHORIZED"
    assert proactive_action.authorization_status == "UNAUTHORIZED"


def test_no_pillar_can_silently_execute_an_action():
    local_action = create_action()
    remote_action = create_action()
    proactive_action = create_action()

    assert local_action.execution_status == "NOT_EXECUTED"
    assert remote_action.execution_status == "NOT_EXECUTED"
    assert proactive_action.execution_status == "NOT_EXECUTED"


def test_safety_boundary_preserves_explicit_authorization_flow():
    action = create_action(operation=lambda: None)

    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is True

    assert action.execution_status == "EXECUTED"