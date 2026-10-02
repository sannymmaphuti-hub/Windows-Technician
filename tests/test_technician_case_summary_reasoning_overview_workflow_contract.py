from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


def create_summaries():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(workflow)
    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    return (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    )


def add_evidence(case):
    case.findings.extend(
        ["finding-1", "finding-2"]
    )
    case.correlations.append(
        "correlation-1"
    )
    case.root_causes.append(
        "root-cause-1"
    )
    case.recommendations.extend(
        ["recommendation-1", "recommendation-2"]
    )


def test_workflow_progression_does_not_change_reasoning_evidence():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    add_evidence(case)

    expected = reasoning_summary.overview

    assert workflow.state is WorkflowState.OPEN

    workflow.start_investigation()
    assert reasoning_summary.overview == expected

    workflow.mark_diagnosed()
    assert reasoning_summary.overview == expected

    workflow.require_action()
    assert reasoning_summary.overview == expected

    workflow.start_remediation()
    assert reasoning_summary.overview == expected

    workflow.start_verification()
    assert reasoning_summary.overview == expected

    workflow.resolve()
    assert reasoning_summary.overview == expected

    assert (
        case_summary.reasoning_summary.overview
        == expected
    )


def test_every_workflow_state_preserves_same_case_identity():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case_id = reasoning_summary.case_id
    workflow_id = reasoning_summary.workflow_id

    assert case_summary.case_id == case_id
    assert case_summary.workflow_id == workflow_id

    workflow.start_investigation()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    workflow.mark_diagnosed()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    workflow.require_action()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    workflow.start_remediation()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    workflow.start_verification()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    workflow.resolve()
    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id


def test_overview_does_not_become_workflow_state_snapshot():
    (
        _,
        workflow,
        reasoning_summary,
        _,
    ) = create_summaries()

    states = [
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
        WorkflowState.DIAGNOSED,
        WorkflowState.ACTION_REQUIRED,
        WorkflowState.REMEDIATING,
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
    ]

    assert workflow.state is states[0]

    for state in states[1:]:
        if state is WorkflowState.INVESTIGATING:
            workflow.start_investigation()
        elif state is WorkflowState.DIAGNOSED:
            workflow.mark_diagnosed()
        elif state is WorkflowState.ACTION_REQUIRED:
            workflow.require_action()
        elif state is WorkflowState.REMEDIATING:
            workflow.start_remediation()
        elif state is WorkflowState.VERIFYING:
            workflow.start_verification()
        elif state is WorkflowState.RESOLVED:
            workflow.resolve()

        overview = reasoning_summary.overview

        assert "workflow_state" not in overview
        assert "state" not in overview
        assert "is_terminal" not in overview


def test_workflow_transitions_do_not_duplicate_reasoning_evidence():
    (
        case,
        workflow,
        reasoning_summary,
        _,
    ) = create_summaries()

    add_evidence(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    overview = reasoning_summary.overview

    assert overview["finding_count"] == 2
    assert overview["correlation_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["recommendation_count"] == 2

    assert overview["findings"] == [
        "finding-1",
        "finding-2",
    ]

    assert overview["correlations"] == [
        "correlation-1",
    ]

    assert overview["root_causes"] == [
        "root-cause-1",
    ]

    assert overview["recommendations"] == [
        "recommendation-1",
        "recommendation-2",
    ]


def test_case_summary_and_reasoning_summary_remain_synchronized_through_workflow():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    add_evidence(case)

    assert (
        case_summary.reasoning_summary
        is reasoning_summary
    )

    workflow.start_investigation()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    workflow.mark_diagnosed()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    workflow.require_action()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    workflow.start_remediation()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    workflow.start_verification()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    workflow.resolve()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_workflow_history_does_not_appear_in_reasoning_overview():
    (
        _,
        workflow,
        reasoning_summary,
        _,
    ) = create_summaries()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    overview = reasoning_summary.overview

    assert "workflow_history" not in overview
    assert "history" not in overview
    assert "transitions" not in overview


def test_terminal_transition_preserves_reasoning_summary_identity():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    add_evidence(case)

    assert case_summary.reasoning_summary is reasoning_summary

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.is_terminal is True
    assert case_summary.reasoning_summary is reasoning_summary
    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )