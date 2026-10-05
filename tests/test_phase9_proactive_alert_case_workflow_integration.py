from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.case_timeline import CaseTimeline


def create_proactive_chain():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="TEST-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

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


def create_workflow():
    _, _, _, case = create_proactive_chain()
    return TechnicianWorkflow(case)


def progress_to_verification(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()


# ============================================================
# PROACTIVE ALERT
# ============================================================


def test_proactive_alert_is_created():
    machine, alert, _, _ = create_proactive_chain()

    assert alert.machine is machine
    assert alert.machine_id == machine.machine_id
    assert alert.hostname == machine.hostname


def test_proactive_alert_starts_active():
    _, alert, _, _ = create_proactive_chain()

    assert alert.status == "ACTIVE"


def test_proactive_alert_contains_detection_context():
    _, alert, _, _ = create_proactive_chain()

    assert alert.alert_type == "PERFORMANCE_DEGRADATION"
    assert alert.metric == "cpu_usage"
    assert alert.message


# ============================================================
# PROACTIVE RECOMMENDATION
# ============================================================


def test_proactive_recommendation_belongs_to_alert():
    _, alert, recommendation, _ = create_proactive_chain()

    assert recommendation.alert is alert


def test_proactive_recommendation_preserves_machine_identity():
    machine, _, recommendation, _ = create_proactive_chain()

    assert recommendation.machine_id == machine.machine_id
    assert recommendation.hostname == machine.hostname


def test_proactive_recommendation_starts_pending():
    _, _, recommendation, _ = create_proactive_chain()

    assert recommendation.status == "PENDING"


def test_proactive_recommendation_contains_action_guidance():
    _, _, recommendation, _ = create_proactive_chain()

    assert recommendation.recommendation == (
        "Investigate sustained CPU usage."
    )


# ============================================================
# PROACTIVE CASE CREATION
# ============================================================


def test_proactive_case_is_created_from_recommendation():
    _, _, recommendation, case = create_proactive_chain()

    assert case is not None
    assert case.proactive_recommendation is recommendation


def test_proactive_case_preserves_alert():
    _, alert, _, case = create_proactive_chain()

    assert case.proactive_alert is alert


def test_proactive_case_preserves_machine_identity():
    machine, _, _, case = create_proactive_chain()

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname


def test_proactive_case_has_case_identity():
    _, _, _, case = create_proactive_chain()

    assert case.case_id is not None


def test_proactive_case_is_independent_case_object():
    _, _, _, case = create_proactive_chain()

    assert case.__class__.__name__ == "DiagnosticCase"


# ============================================================
# CASE → TECHNICIAN WORKFLOW
# ============================================================


def test_proactive_case_can_enter_technician_workflow():
    workflow = create_workflow()

    assert workflow.case is not None
    assert workflow.case.proactive_alert is not None


def test_proactive_workflow_starts_open():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN


def test_proactive_case_can_start_investigation():
    workflow = create_workflow()

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_case_can_be_diagnosed():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_proactive_case_can_require_action():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


# ============================================================
# PROACTIVE CASE → REMEDIATION WORKFLOW
# ============================================================


def test_proactive_case_can_enter_remediation():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_proactive_case_can_enter_verification():
    workflow = create_workflow()

    progress_to_verification(workflow)

    assert workflow.state is WorkflowState.VERIFYING


def test_proactive_case_can_be_resolved():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


# ============================================================
# PROACTIVE CASE TIMELINE
# ============================================================


def test_proactive_case_timeline_uses_existing_workflow():
    workflow = create_workflow()
    timeline = CaseTimeline(workflow)

    assert timeline.workflow is workflow


def test_proactive_case_timeline_exposes_case_identity():
    workflow = create_workflow()
    timeline = CaseTimeline(workflow)

    assert timeline.case_id == workflow.case.case_id
    assert timeline.machine_id == workflow.case.machine_id
    assert timeline.hostname == workflow.case.hostname


def test_proactive_case_timeline_exposes_workflow_state():
    workflow = create_workflow()
    timeline = CaseTimeline(workflow)

    assert timeline.state is WorkflowState.OPEN


# ============================================================
# HISTORY PRESERVATION
# ============================================================


def test_proactive_case_workflow_preserves_history():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    assert len(workflow.history) == 6


def test_proactive_case_history_contains_full_lifecycle():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    expected_states = [
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

    assert workflow.history == expected_states


# ============================================================
# TERMINAL STATE
# ============================================================


def test_proactive_case_becomes_terminal_when_resolved():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    assert workflow.is_terminal is True


def test_proactive_case_timeline_reflects_terminal_state():
    workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    timeline = CaseTimeline(workflow)

    assert timeline.is_terminal is True
    assert timeline.state is WorkflowState.RESOLVED