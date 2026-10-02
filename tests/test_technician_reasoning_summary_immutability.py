from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary, workflow, history


def test_workflow_cannot_be_replaced():
    summary, workflow, _ = create_summary()

    try:
        summary.workflow = None
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "workflow reference must not be replaceable."
        )

    assert summary.workflow is workflow


def test_cycle_history_cannot_be_replaced():
    summary, _, history = create_summary()

    try:
        summary.cycle_history = None
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "cycle_history reference must not be replaceable."
        )

    assert summary.cycle_history is history


def test_case_id_cannot_be_replaced():
    summary, _, _ = create_summary()

    try:
        summary.case_id = "replacement"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "case_id must not be replaceable."
        )


def test_workflow_id_cannot_be_replaced():
    summary, _, _ = create_summary()

    try:
        summary.workflow_id = "replacement"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "workflow_id must not be replaceable."
        )


def test_summary_references_remain_stable():
    summary, workflow, history = create_summary()

    assert summary.workflow is workflow
    assert summary.cycle_history is history