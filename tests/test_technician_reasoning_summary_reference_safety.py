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


def test_workflow_reference_is_read_only():
    summary, workflow, _ = create_summary()

    try:
        summary.workflow = TechnicianWorkflow(
            DiagnosticCase()
        )
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "workflow reference must be read-only."
        )

    assert summary.workflow is workflow


def test_cycle_history_reference_is_read_only():
    summary, _, history = create_summary()

    try:
        summary.cycle_history = None
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "cycle_history reference must be read-only."
        )

    assert summary.cycle_history is history


def test_workflow_reference_remains_identical():
    summary, workflow, _ = create_summary()

    assert summary.workflow is workflow


def test_cycle_history_reference_remains_identical():
    summary, _, history = create_summary()

    assert summary.cycle_history is history