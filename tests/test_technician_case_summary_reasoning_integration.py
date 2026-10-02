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

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    case_summary = TechnicianCaseSummary(
        workflow
    )

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


def test_case_summary_can_hold_reasoning_summary():
    (
        _,
        _,
        _,
        case_summary,
        reasoning_summary,
    ) = create_context()

    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    assert (
        case_summary.reasoning_summary
        is reasoning_summary
    )


def test_case_summary_reasoning_summary_uses_same_workflow():
    (
        _,
        workflow,
        _,
        case_summary,
        reasoning_summary,
    ) = create_context()

    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    assert (
        case_summary.reasoning_summary.workflow
        is workflow
    )


def test_case_summary_rejects_invalid_reasoning_summary():
    (
        _,
        _,
        _,
        case_summary,
        _,
    ) = create_context()

    with pytest.raises(ValueError):
        case_summary.set_reasoning_summary(
            None
        )


def test_case_summary_rejects_reasoning_summary_from_different_workflow():
    (
        _,
        _,
        _,
        case_summary,
        _,
    ) = create_context()

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(
        other_case
    )
    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    other_reasoning_summary = TechnicianReasoningSummary(
        other_workflow,
        other_history,
    )

    with pytest.raises(ValueError):
        case_summary.set_reasoning_summary(
            other_reasoning_summary
        )


def test_case_summary_reasoning_summary_defaults_to_none():
    (
        _,
        _,
        _,
        case_summary,
        _,
    ) = create_context()

    assert case_summary.reasoning_summary is None