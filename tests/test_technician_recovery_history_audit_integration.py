import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(
        TechnicianReasoningSummary(workflow, history)
    )
    return summary


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def complete_lifecycle(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def complete_reopened_lifecycle(workflow):
    workflow.reopen()
    complete_lifecycle(workflow)


def test_recovery_history_provides_complete_audit_sequence():
    workflow = build_workflow()
    history = build_history(workflow)

    recorded_cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
        record_cycle(workflow, history, 4),
    ]

    assert history.cycle_count == 5
    assert history.cycles[0].cycle_number == 0

    for index, cycle in enumerate(recorded_cycles, start=1):
        assert history.cycles[index] is cycle


def test_recovery_history_audit_sequence_preserves_cycle_order():
    workflow = build_workflow()
    history = build_history(workflow)

    for cycle_number in range(1, 8):
        record_cycle(workflow, history, cycle_number)

    assert [cycle.cycle_number for cycle in history.cycles] == list(
        range(8)
    )


def test_recovery_history_audit_reads_do_not_create_cycles():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    initial_count = history.cycle_count
    first_read = list(history.cycles)
    second_read = list(history.cycles)
    third_read = list(history.cycles)

    assert history.cycle_count == initial_count
    assert first_read == second_read == third_read
    assert first_read[1] is first
    assert first_read[2] is second


def test_workflow_activity_does_not_rewrite_recovery_audit_history():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(4):
        complete_reopened_lifecycle(workflow)

    assert history.cycle_count == 3
    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert [cycle.cycle_number for cycle in history.cycles] == [
        0,
        1,
        2,
    ]


def test_reopening_and_reinvestigation_preserve_previous_audit_records():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second = record_cycle(workflow, history, 2)

    assert history.cycle_count == 3
    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert first.cycle_number == 1
    assert second.cycle_number == 2


def test_escalation_preserves_recovery_audit_history():
    workflow = build_workflow()
    history = build_history(workflow)

    cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
    ]

    workflow.start_investigation()
    workflow.escalate()

    assert workflow.state.name == "ESCALATED"
    assert history.cycle_count == 4

    for index, cycle in enumerate(cycles, start=1):
        assert history.cycles[index] is cycle

    assert [cycle.cycle_number for cycle in history.cycles] == [
        0,
        1,
        2,
        3,
    ]


def test_failed_workflow_operations_do_not_corrupt_audit_history():
    workflow = build_workflow()
    history = build_history(workflow)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.require_action()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert history.cycle_count == 3
    assert history.cycles[1] is first
    assert history.cycles[2] is second
    assert [cycle.cycle_number for cycle in history.cycles] == [
        0,
        1,
        2,
    ]


def test_case_summary_and_recovery_history_share_same_audit_source():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    summary_history = summary.reasoning_summary.cycle_history

    assert summary_history is history
    assert summary_history.cycles[1] is first
    assert summary_history.cycles[2] is second
    assert summary_history.cycle_count == history.cycle_count


def test_recovery_audit_history_remains_separate_from_workflow_audit_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    assert summary.workflow_history is not history
    assert summary.reasoning_summary.cycle_history is history
    assert history.cycle_count == 3
    assert len(workflow.history) > history.cycle_count


def test_long_recovery_sequence_remains_auditable_after_all_activity():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    expected_cycles = []

    for cycle_number in range(1, 11):
        expected_cycles.append(
            record_cycle(workflow, history, cycle_number)
        )

        if cycle_number < 10:
            complete_reopened_lifecycle(workflow)

    first_snapshot = list(history.cycles)

    for _ in range(5):
        summary.reasoning_summary.cycle_history.cycles
        list(summary.reasoning_summary.cycle_history.cycles)
        list(history.cycles)

    final_snapshot = list(history.cycles)

    assert history.cycle_count == 11
    assert first_snapshot == final_snapshot
    assert first_snapshot[0].cycle_number == 0

    for index, expected_cycle in enumerate(expected_cycles, start=1):
        assert first_snapshot[index] is expected_cycle
        assert final_snapshot[index] is expected_cycle

    assert [cycle.cycle_number for cycle in final_snapshot] == list(
        range(11)
    )