import pytest

from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.remediation_action import RemediationAction
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor


# ============================================================
# FACTORIES
# ============================================================


def create_machine(
    machine_id="machine-001",
    hostname="TEST-PC",
):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="Windows",
        operating_system="Windows 11",
    )


def create_alert(
    machine=None,
    alert_type="MEMORY_PRESSURE",
    metric="memory_usage",
    message="Memory usage is above the expected baseline.",
):
    if machine is None:
        machine = create_machine()

    return ProactiveAlert(
        machine=machine,
        alert_type=alert_type,
        metric=metric,
        message=message,
    )


def create_recommendation(
    alert=None,
    recommendation="Review memory-consuming applications.",
):
    if alert is None:
        alert = create_alert()

    return ProactiveRecommendation(
        alert=alert,
        recommendation=recommendation,
    )


def create_case(
    recommendation=None,
):
    if recommendation is None:
        recommendation = create_recommendation()

    return ProactiveCaseCreator().create(recommendation)


def create_workflow(
    recommendation=None,
):
    return TechnicianWorkflow(create_case(recommendation))


def create_action(
    action_id="action-001",
    operation=None,
):
    return RemediationAction(
        action_id=action_id,
        description="Proactive safety test action.",
        requires_authorization=True,
        operation=operation,
    )


def create_remote_environment():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


# ============================================================
# PROACTIVE ALERT SAFETY
# ============================================================


def test_proactive_alert_starts_active():
    alert = create_alert()

    assert alert.status == "ACTIVE"


def test_proactive_alert_does_not_have_remediation_authority():
    alert = create_alert()

    assert not hasattr(alert, "execute")
    assert not hasattr(alert, "authorize")


def test_acknowledging_alert_does_not_execute_anything():
    executions = []

    alert = create_alert()
    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"
    assert executions == []


def test_resolving_alert_does_not_execute_anything():
    executions = []

    alert = create_alert()
    alert.resolve()

    assert alert.status == "RESOLVED"
    assert executions == []


def test_dismissing_alert_does_not_execute_anything():
    executions = []

    alert = create_alert()
    alert.dismiss()

    assert alert.status == "DISMISSED"
    assert executions == []


def test_alert_does_not_authorize_remediation_action():
    alert = create_alert()
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"

    alert.acknowledge()

    assert action.authorization_status == "UNAUTHORIZED"


# ============================================================
# PROACTIVE RECOMMENDATION SAFETY
# ============================================================


def test_recommendation_starts_pending():
    recommendation = create_recommendation()

    assert recommendation.status == "PENDING"


def test_recommendation_contains_no_execution_authority():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "execute")
    assert not hasattr(recommendation, "authorize")


def test_acknowledging_recommendation_does_not_execute_remediation():
    executions = []

    recommendation = create_recommendation()
    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"
    assert executions == []


def test_dismissing_recommendation_does_not_execute_remediation():
    executions = []

    recommendation = create_recommendation()
    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert executions == []


def test_recommendation_does_not_authorize_action():
    recommendation = create_recommendation()
    action = create_action()

    recommendation.acknowledge()

    assert action.authorization_status == "UNAUTHORIZED"


def test_recommendation_does_not_execute_action():
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    recommendation.acknowledge()

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


# ============================================================
# PROACTIVE CASE CREATION SAFETY
# ============================================================


def test_proactive_case_contains_recommendation():
    recommendation = create_recommendation()
    case = create_case(recommendation)

    assert case.proactive_recommendation is recommendation


def test_proactive_case_contains_alert():
    recommendation = create_recommendation()
    case = create_case(recommendation)

    assert case.proactive_alert is recommendation.alert


def test_proactive_case_preserves_machine_identity():
    machine = create_machine("machine-a", "PC-A")
    alert = create_alert(machine=machine)
    recommendation = create_recommendation(alert=alert)

    case = create_case(recommendation)

    assert case.machine_id == "machine-a"
    assert case.hostname == "PC-A"


def test_proactive_case_creation_does_not_execute_remediation():
    executions = []

    recommendation = create_recommendation()
    case = create_case(recommendation)

    action = create_action(
        operation=lambda: executions.append(True),
    )

    assert case is not None
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_proactive_case_creation_does_not_authorize_action():
    recommendation = create_recommendation()
    create_case(recommendation)

    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


# ============================================================
# CASE → WORKFLOW SAFETY
# ============================================================


def test_proactive_workflow_starts_open():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN


def test_proactive_case_creation_does_not_start_investigation():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_proactive_workflow_requires_explicit_investigation():
    workflow = create_workflow()

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_alert_does_not_start_workflow():
    alert = create_alert()
    case = create_case(create_recommendation(alert))
    workflow = TechnicianWorkflow(case)

    alert.acknowledge()

    assert workflow.state is WorkflowState.OPEN


def test_proactive_recommendation_does_not_start_workflow():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.acknowledge()

    assert workflow.state is WorkflowState.OPEN


# ============================================================
# PROACTIVE WORKFLOW BYPASS PROTECTION
# ============================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "mark_diagnosed",
        "require_action",
        "start_remediation",
        "start_verification",
        "resolve",
    ],
)
def test_proactive_workflow_cannot_skip_from_open(method_name):
    workflow = create_workflow()

    with pytest.raises(ValueError):
        getattr(workflow, method_name)()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_proactive_workflow_cannot_resolve_without_investigation():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.OPEN


def test_proactive_workflow_cannot_start_remediation_from_open():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.OPEN


# ============================================================
# PROACTIVE RECOMMENDATION ≠ AUTHORIZATION
# ============================================================


def test_pending_recommendation_does_not_authorize_action():
    recommendation = create_recommendation()
    action = create_action()

    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_acknowledged_recommendation_does_not_authorize_action():
    recommendation = create_recommendation()
    action = create_action()

    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_dismissed_recommendation_does_not_authorize_action():
    recommendation = create_recommendation()
    action = create_action()

    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_resolved_alert_does_not_authorize_action():
    alert = create_alert()
    action = create_action()

    alert.resolve()

    assert alert.status == "RESOLVED"
    assert action.authorization_status == "UNAUTHORIZED"


# ============================================================
# PROACTIVE RECOMMENDATION ≠ EXECUTION
# ============================================================


def test_pending_recommendation_cannot_execute_action():
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

    assert recommendation.status == "PENDING"


def test_acknowledged_recommendation_cannot_execute_action():
    executions = []

    recommendation = create_recommendation()
    recommendation.acknowledge()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_dismissed_recommendation_cannot_execute_action():
    executions = []

    recommendation = create_recommendation()
    recommendation.dismiss()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


# ============================================================
# EXPLICIT AUTHORIZATION STILL REQUIRED
# ============================================================


def test_proactive_path_does_not_change_action_authorization_state():
    recommendation = create_recommendation()
    action = create_action()

    recommendation.acknowledge()

    assert action.authorization_status == "UNAUTHORIZED"

    recommendation.dismiss()

    assert action.authorization_status == "UNAUTHORIZED"


def test_action_requires_explicit_authorization_before_execution():
    executions = []

    action = create_action(
        operation=lambda: executions.append(True),
    )

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_explicit_authorization_is_separate_from_proactive_recommendation():
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    recommendation.acknowledge()

    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_authorization_then_execution_remains_explicit():
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    recommendation.acknowledge()
    action.authorize()

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

    assert action.execute() is True

    assert action.execution_status == "EXECUTED"
    assert executions == [True]


# ============================================================
# ALERT LIFECYCLE DOES NOT CONTROL REMEDIATION
# ============================================================


@pytest.mark.parametrize(
    "alert_method",
    [
        "acknowledge",
        "resolve",
        "dismiss",
    ],
)
def test_alert_lifecycle_never_executes_action(alert_method):
    executions = []

    alert = create_alert()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    getattr(alert, alert_method)()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


@pytest.mark.parametrize(
    "recommendation_method",
    [
        "acknowledge",
        "dismiss",
    ],
)
def test_recommendation_lifecycle_never_executes_action(
    recommendation_method,
):
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    getattr(recommendation, recommendation_method)()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


# ============================================================
# MULTI-MACHINE PROACTIVE ISOLATION
# ============================================================


def test_proactive_alert_preserves_machine_a_identity():
    machine_a = create_machine("machine-a", "PC-A")
    alert = create_alert(machine=machine_a)

    assert alert.machine_id == "machine-a"
    assert alert.hostname == "PC-A"


def test_proactive_alert_does_not_change_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    alert = create_alert(machine=machine_a)
    alert.acknowledge()

    assert alert.machine_id == "machine-a"
    assert machine_b.connection_state == "UNKNOWN"


def test_two_proactive_alerts_keep_machine_identity_separate():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    alert_a = create_alert(machine=machine_a)
    alert_b = create_alert(machine=machine_b)

    assert alert_a.machine_id == "machine-a"
    assert alert_b.machine_id == "machine-b"
    assert alert_a.machine_id != alert_b.machine_id


def test_proactive_recommendations_keep_machine_identity_separate():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    recommendation_a = create_recommendation(
        alert=create_alert(machine=machine_a),
    )

    recommendation_b = create_recommendation(
        alert=create_alert(machine=machine_b),
    )

    assert recommendation_a.machine_id == "machine-a"
    assert recommendation_b.machine_id == "machine-b"
    assert recommendation_a.machine_id != recommendation_b.machine_id


def test_proactive_cases_keep_machine_identity_separate():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    case_a = create_case(
        create_recommendation(
            create_alert(machine=machine_a),
        )
    )

    case_b = create_case(
        create_recommendation(
            create_alert(machine=machine_b),
        )
    )

    assert case_a.machine_id == "machine-a"
    assert case_b.machine_id == "machine-b"
    assert case_a.machine_id != case_b.machine_id


# ============================================================
# PROACTIVE + REMOTE SAFETY
# ============================================================


def test_proactive_alert_does_not_connect_machine():
    machine = create_machine()

    assert machine.connection_state == "UNKNOWN"

    create_alert(machine=machine)

    assert machine.connection_state == "UNKNOWN"


def test_proactive_recommendation_does_not_connect_machine():
    machine = create_machine()

    recommendation = create_recommendation(
        alert=create_alert(machine=machine),
    )

    assert recommendation.machine_id == machine.machine_id
    assert machine.connection_state == "UNKNOWN"


def test_proactive_case_creation_does_not_connect_machine():
    machine = create_machine()

    create_case(
        create_recommendation(
            create_alert(machine=machine),
        )
    )

    assert machine.connection_state == "UNKNOWN"


def test_proactive_path_cannot_create_remote_context_while_disconnected():
    machine = create_machine()

    create_case(
        create_recommendation(
            create_alert(machine=machine),
        )
    )

    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine,
            session=session,
        )


def test_proactive_case_creation_does_not_create_remote_session():
    machine = create_machine()

    case = create_case(
        create_recommendation(
            create_alert(machine=machine),
        )
    )

    assert case.machine_id == machine.machine_id
    assert machine.connection_state == "UNKNOWN"


# ============================================================
# REMOTE EXECUTION STILL REQUIRES AUTHORIZATION
# ============================================================


def test_proactive_case_does_not_authorize_remote_action():
    machine, session, context = create_remote_environment()

    recommendation = create_recommendation(
        alert=create_alert(machine=machine),
    )

    case = create_case(recommendation)

    action = create_action(
        operation=lambda: None,
    )

    recommendation.acknowledge()

    assert case.proactive_recommendation is recommendation
    assert action.authorization_status == "UNAUTHORIZED"

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_execution_requires_explicit_authorization_after_proactive_detection():
    machine, session, context = create_remote_environment()

    recommendation = create_recommendation(
        alert=create_alert(machine=machine),
    )

    recommendation.acknowledge()

    executions = []

    action = create_action(
        operation=lambda: executions.append(True),
    )

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

    action.authorize()

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"
    assert executions == [True]


# ============================================================
# PROACTIVE STATE TRANSITIONS
# ============================================================


def test_alert_acknowledgement_does_not_change_case_state():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.alert.acknowledge()

    assert workflow.state is WorkflowState.OPEN


def test_recommendation_acknowledgement_does_not_change_case_state():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.acknowledge()

    assert workflow.state is WorkflowState.OPEN


def test_alert_resolution_does_not_resolve_workflow():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.alert.resolve()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


def test_alert_dismissal_does_not_resolve_workflow():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.alert.dismiss()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


def test_recommendation_dismissal_does_not_resolve_workflow():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    workflow = TechnicianWorkflow(case)

    recommendation.dismiss()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


# ============================================================
# PROACTIVE PATH REQUIRES NORMAL TECHNICIAN LIFECYCLE
# ============================================================


def test_proactive_case_can_enter_normal_investigation():
    workflow = create_workflow()

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_case_can_follow_normal_diagnostic_path():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_proactive_case_can_require_action_after_diagnosis():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_proactive_case_can_reach_remediation_only_after_required_steps():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_proactive_case_can_reach_verification_only_after_remediation():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING


def test_proactive_case_can_resolve_only_after_verification():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


# ============================================================
# FINAL SAFETY INVARIANTS
# ============================================================


def test_detection_does_not_equal_authorization():
    alert = create_alert()
    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate the detected condition.",
    )
    action = create_action()

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_recommendation_does_not_equal_execution():
    executions = []

    recommendation = create_recommendation()

    action = create_action(
        operation=lambda: executions.append(True),
    )

    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_case_creation_does_not_equal_remediation():
    recommendation = create_recommendation()
    case = create_case(recommendation)
    action = create_action()

    assert case.proactive_recommendation is recommendation
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_proactive_detection_cannot_skip_workflow():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN

    with pytest.raises(ValueError):
        workflow.start_remediation()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.OPEN


def test_proactive_path_preserves_explicit_authorization_boundary():
    recommendation = create_recommendation()
    action = create_action()

    recommendation.acknowledge()

    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_proactive_path_preserves_execution_boundary():
    executions = []

    recommendation = create_recommendation()
    action = create_action(
        operation=lambda: executions.append(True),
    )

    recommendation.acknowledge()
    action.authorize()

    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

    action.execute()

    assert action.execution_status == "EXECUTED"
    assert executions == [True]


def test_proactive_path_does_not_change_machine_connection_state():
    machine = create_machine()

    alert = create_alert(machine=machine)
    recommendation = create_recommendation(alert=alert)
    create_case(recommendation)

    assert machine.connection_state == "UNKNOWN"


def test_proactive_path_does_not_create_hidden_remote_authority():
    machine = create_machine()

    alert = create_alert(machine=machine)
    recommendation = create_recommendation(alert=alert)
    case = create_case(recommendation)

    assert case.machine_id == machine.machine_id
    assert machine.connection_state == "UNKNOWN"

    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"