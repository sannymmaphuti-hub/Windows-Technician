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


def test_summary_exposes_original_cycle_history():
    summary, _, history = create_summary()

    assert summary.cycle_history is history


def test_initial_cycle_is_original():
    summary, _, history = create_summary()

    assert history.cycle_count == 1
    assert history.latest_cycle.is_original is True
    assert summary.cycle_history.latest_cycle.is_original is True


def test_recovery_cycle_is_visible_through_summary():
    summary, workflow, history = create_summary()

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    assert summary.cycle_history.cycle_count == 2
    assert summary.cycle_history.latest_cycle is recovery_cycle


def test_recovery_cycle_number_remains_sequential():
    summary, workflow, history = create_summary()

    workflow.start_investigation()

    first_recovery = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(first_recovery)

    second_recovery = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(second_recovery)

    cycles = summary.cycle_history.cycles

    assert [cycle.cycle_number for cycle in cycles] == [0, 1, 2]