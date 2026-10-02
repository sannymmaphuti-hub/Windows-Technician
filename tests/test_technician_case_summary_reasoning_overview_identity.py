from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summaries():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(workflow)
    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    return case, workflow, reasoning_summary, case_summary


def test_case_summary_reasoning_overview_preserves_case_identity():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert case_summary.case_id == case.case_id
    assert reasoning_summary.case_id == case.case_id
    assert case_summary.reasoning_summary.case_id == case.case_id
    assert workflow.case is case


def test_case_summary_reasoning_overview_preserves_workflow_identity():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert case_summary.workflow_id == workflow.workflow_id
    assert reasoning_summary.workflow_id == workflow.workflow_id
    assert (
        case_summary.reasoning_summary.workflow_id
        == workflow.workflow_id
    )


def test_overview_does_not_create_identity_fields():
    (
        _,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert "case_id" not in overview
    assert "workflow_id" not in overview

    assert overview == reasoning_summary.overview


def test_identity_remains_stable_after_case_evidence_changes():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    original_case_id = case.case_id
    original_workflow_id = workflow.workflow_id

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    assert case_summary.case_id == original_case_id
    assert reasoning_summary.case_id == original_case_id

    assert case_summary.workflow_id == original_workflow_id
    assert reasoning_summary.workflow_id == original_workflow_id

    assert case_summary.reasoning_summary.case_id == original_case_id
    assert (
        case_summary.reasoning_summary.workflow_id
        == original_workflow_id
    )