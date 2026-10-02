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


def complete_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_case_summary_exposes_stable_case_identity():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    assert summary.case_id == case.case_id
    assert summary.case_id == reasoning_summary.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_id == reasoning_summary.workflow_id


def test_case_summary_exposes_current_workflow_state():
    (
        _,
        workflow,
        _,
        _,
        summary,
    ) = create_summary()

    assert summary.workflow_state is WorkflowState.OPEN
    assert summary.is_terminal is False

    workflow.start_investigation()

    assert (
        summary.workflow_state
        is WorkflowState.INVESTIGATING
    )
    assert summary.is_terminal is False

    workflow.mark_diagnosed()

    assert (
        summary.workflow_state
        is WorkflowState.DIAGNOSED
    )

    complete_workflow_from_diagnosed(workflow)

    assert summary.workflow_state is WorkflowState.RESOLVED
    assert summary.is_terminal is True


def complete_workflow_from_diagnosed(workflow):
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_case_summary_evidence_is_live():
    (
        case,
        _,
        _,
        _,
        summary,
    ) = create_summary()

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == ["recommendation"]


def test_case_summary_evidence_collections_are_isolated():
    (
        case,
        _,
        _,
        _,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    findings = summary.findings
    root_causes = summary.root_causes
    recommendations = summary.recommendations

    findings.append("injected")
    root_causes.append("injected")
    recommendations.append("injected")

    assert case.findings == ["finding"]
    assert case.root_causes == ["root-cause"]
    assert case.recommendations == ["recommendation"]


def test_reasoning_summary_is_same_intelligence_boundary():
    (
        _,
        _,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    assert summary.reasoning_summary is reasoning_summary


def test_reasoning_summary_tracks_case_summary_evidence():
    (
        case,
        _,
        _,
        _,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    overview = summary.reasoning_summary.overview

    assert overview["findings"] == summary.findings
    assert overview["root_causes"] == summary.root_causes
    assert (
        overview["recommendations"]
        == summary.recommendations
    )


def test_workflow_state_does_not_replace_case_evidence():
    (
        case,
        workflow,
        _,
        _,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == ["recommendation"]


def test_terminal_summary_preserves_all_contracts():
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

    complete_workflow(workflow)

    assert summary.is_terminal is True
    assert summary.workflow_state is WorkflowState.RESOLVED

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == ["recommendation"]

    assert summary.reasoning_summary is reasoning_summary

    assert (
        summary.reasoning_summary.overview["findings"]
        == ["finding"]
    )

    assert (
        summary.reasoning_summary.overview["root_causes"]
        == ["root-cause"]
    )

    assert (
        summary.reasoning_summary.overview["recommendations"]
        == ["recommendation"]
    )


def test_workflow_history_is_available_without_becoming_reasoning_data():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert summary.workflow_history == workflow.history

    overview = reasoning_summary.overview

    assert "workflow_history" not in overview
    assert "history" not in overview
    assert "transitions" not in overview


def test_case_summary_does_not_duplicate_reasoning_summary():
    (
        _,
        _,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    assert summary.reasoning_summary is reasoning_summary

    first = summary.reasoning_summary.overview
    second = reasoning_summary.overview

    assert first == second
    assert first is not second


def test_case_summary_identity_survives_workflow_completion():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        summary,
    ) = create_summary()

    case_id = summary.case_id
    workflow_id = summary.workflow_id

    complete_workflow(workflow)

    assert summary.case_id == case_id
    assert summary.workflow_id == workflow_id

    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id