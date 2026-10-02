import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_context():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    history = TechnicianRecoveryCycleHistory(workflow)

    case_summary = TechnicianCaseSummary(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return (
        case,
        workflow,
        history,
        case_summary,
        reasoning_summary,
    )


def test_case_summary_and_reasoning_summary_share_workflow():
    (
        _,
        workflow,
        _,
        case_summary,
        reasoning_summary,
    ) = create_context()

    assert case_summary.workflow is workflow
    assert reasoning_summary.workflow is workflow


def test_case_summary_and_reasoning_summary_share_case():
    (
        case,
        _,
        _,
        case_summary,
        reasoning_summary,
    ) = create_context()

    assert case_summary.workflow.case is case
    assert reasoning_summary.workflow.case is case


def test_reasoning_summary_uses_same_cycle_history():
    (
        _,
        _,
        history,
        _,
        reasoning_summary,
    ) = create_context()

    assert reasoning_summary.cycle_history is history


def test_reasoning_summary_reads_existing_case_data():
    (
        case,
        _,
        _,
        _,
        reasoning_summary,
    ) = create_context()

    assert reasoning_summary.findings == case.findings
    assert reasoning_summary.correlations == case.correlations
    assert reasoning_summary.root_causes == case.root_causes
    assert reasoning_summary.recommendations == case.recommendations


def test_empty_case_has_zero_reasoning_counts():
    (
        _,
        _,
        _,
        _,
        reasoning_summary,
    ) = create_context()

    assert reasoning_summary.finding_count == 0
    assert reasoning_summary.correlation_count == 0
    assert reasoning_summary.root_cause_count == 0
    assert reasoning_summary.recommendation_count == 0


def test_reasoning_summary_does_not_replace_case_summary():
    (
        _,
        _,
        _,
        case_summary,
        reasoning_summary,
    ) = create_context()

    assert isinstance(
        case_summary,
        TechnicianCaseSummary,
    )

    assert isinstance(
        reasoning_summary,
        TechnicianReasoningSummary,
    )

    assert case_summary is not reasoning_summary