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


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        summary,
    )


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_case_summary_survives_complete_reopen_lifecycle():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    case_id = summary.case_id
    workflow_id = summary.workflow_id

    assert summary.workflow_state is WorkflowState.OPEN
    assert summary.is_terminal is False

    workflow.start_investigation()

    assert (
        summary.workflow_state
        is WorkflowState.INVESTIGATING
    )

    workflow.mark_diagnosed()

    assert (
        summary.workflow_state
        is WorkflowState.DIAGNOSED
    )

    workflow.require_action()

    assert (
        summary.workflow_state
        is WorkflowState.ACTION_REQUIRED
    )

    workflow.start_remediation()

    assert (
        summary.workflow_state
        is WorkflowState.REMEDIATING
    )

    workflow.start_verification()

    assert (
        summary.workflow_state
        is WorkflowState.VERIFYING
    )

    workflow.resolve()

    assert summary.workflow_state is WorkflowState.RESOLVED
    assert summary.is_terminal is True

    workflow.reopen()

    assert (
        summary.workflow_state
        is WorkflowState.INVESTIGATING
    )
    assert summary.is_terminal is False

    assert summary.case_id == case_id
    assert summary.workflow_id == workflow_id

    assert summary.reasoning_summary is reasoning_summary

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == ["recommendation"]

    assert history.cycle_count == 1


def test_reopening_does_not_duplicate_reasoning_evidence():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    before = reasoning_summary.overview

    workflow.reopen()

    after = reasoning_summary.overview

    assert after == before

    assert after["finding_count"] == 1
    assert after["root_cause_count"] == 1
    assert after["recommendation_count"] == 1

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == ["recommendation"]


def test_reopened_workflow_keeps_reasoning_identity():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    case_id = reasoning_summary.case_id
    workflow_id = reasoning_summary.workflow_id

    resolve_workflow(workflow)

    workflow.reopen()

    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id

    assert summary.case_id == case_id
    assert summary.workflow_id == workflow_id

    assert summary.reasoning_summary is reasoning_summary


def test_reopened_workflow_does_not_put_workflow_state_into_overview():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        _,
    ) = create_summary()

    resolve_workflow(workflow)
    workflow.reopen()

    overview = reasoning_summary.overview

    assert workflow.state is WorkflowState.INVESTIGATING

    assert "workflow_state" not in overview
    assert "state" not in overview
    assert "is_terminal" not in overview


def test_reopened_case_can_receive_new_evidence_without_duplication():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("original-finding")

    resolve_workflow(workflow)
    workflow.reopen()

    case.findings.append("reopened-finding")

    overview = reasoning_summary.overview

    assert overview["finding_count"] == 2
    assert overview["findings"] == [
        "original-finding",
        "reopened-finding",
    ]

    assert summary.findings == [
        "original-finding",
        "reopened-finding",
    ]


def test_reopened_case_summary_remains_live():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    resolve_workflow(workflow)
    workflow.reopen()

    case.root_causes.append("new-root-cause")
    case.recommendations.append("new-recommendation")

    assert summary.root_causes == ["new-root-cause"]
    assert summary.recommendations == [
        "new-recommendation"
    ]

    assert (
        reasoning_summary.overview["root_causes"]
        == ["new-root-cause"]
    )

    assert (
        reasoning_summary.overview["recommendations"]
        == ["new-recommendation"]
    )


def test_reopen_history_does_not_replace_workflow_history():
    (
        _,
        workflow,
        _,
        _,
        summary,
    ) = create_summary()

    resolve_workflow(workflow)

    history_before = summary.workflow_history

    workflow.reopen()

    history_after = summary.workflow_history

    assert len(history_after) == len(history_before) + 1
    assert history_after[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_reopened_case_summary_remains_consistent_with_reasoning():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)
    workflow.reopen()

    assert (
        summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    assert (
        summary.reasoning_summary.overview["findings"]
        == summary.findings
    )

    assert (
        summary.reasoning_summary.overview["correlations"]
        == case.correlations
    )

    assert (
        summary.reasoning_summary.overview["root_causes"]
        == summary.root_causes
    )

    assert (
        summary.reasoning_summary.overview["recommendations"]
        == summary.recommendations
    )