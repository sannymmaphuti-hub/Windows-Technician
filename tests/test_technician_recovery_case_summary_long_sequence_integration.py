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


def test_case_summary_exposes_recovery_history_after_long_workflow_sequence():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(5):
        complete_reopened_lifecycle(workflow)

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second
    assert [cycle.cycle_number for cycle in cycle_history.cycles] == [
        0,
        1,
        2,
    ]


def test_case_summary_recovery_history_matches_history_object():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)
    record_cycle(workflow, history, 3)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    assert summary.reasoning_summary.cycle_history is history


def test_case_summary_does_not_duplicate_cycles_after_repeated_reads():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(4):
        complete_reopened_lifecycle(workflow)

    first_read = list(summary.reasoning_summary.cycle_history.cycles)
    second_read = list(summary.reasoning_summary.cycle_history.cycles)
    third_read = list(summary.reasoning_summary.cycle_history.cycles)

    assert first_read == second_read == third_read
    assert [cycle.cycle_number for cycle in third_read] == [0, 1, 2]


def test_new_recovery_cycle_appears_in_case_summary_only_after_explicit_record():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    assert summary.reasoning_summary.cycle_history.cycle_count == 2
    assert summary.reasoning_summary.cycle_history.latest_cycle is first

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    assert summary.reasoning_summary.cycle_history.cycle_count == 2

    second = record_cycle(workflow, history, 2)

    assert summary.reasoning_summary.cycle_history.cycle_count == 3
    assert summary.reasoning_summary.cycle_history.cycles[1] is first
    assert summary.reasoning_summary.cycle_history.cycles[2] is second


def test_case_summary_preserves_recovery_history_after_escalation():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    workflow.reopen()
    workflow.escalate()

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second
    assert [cycle.cycle_number for cycle in cycle_history.cycles] == [
        0,
        1,
        2,
    ]


def test_case_summary_recovery_history_remains_separate_from_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(3):
        complete_reopened_lifecycle(workflow)

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history is history
    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second
    assert summary.workflow_history is not cycle_history


def test_case_summary_does_not_convert_recovery_cycles_into_diagnostic_content():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(2):
        complete_reopened_lifecycle(workflow)

    assert summary.reasoning_summary.cycle_history.cycle_count == 3
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.reasoning_summary.correlations == []


def test_case_summary_preserves_cycle_identity_after_multiple_records():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
        record_cycle(workflow, history, 4),
    ]

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(5):
        complete_reopened_lifecycle(workflow)

    cycle_history = summary.reasoning_summary.cycle_history

    for index, cycle in enumerate(cycles, start=1):
        assert cycle_history.cycles[index] is cycle


def test_case_summary_preserves_recovery_history_through_failed_operations():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second
    assert [cycle.cycle_number for cycle in cycle_history.cycles] == [
        0,
        1,
        2,
    ]


def test_final_case_summary_contains_all_recovery_cycles_after_long_sequence():
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

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycle_count == 11
    assert cycle_history.cycles[0].cycle_number == 0

    for index, expected_cycle in enumerate(expected_cycles, start=1):
        assert cycle_history.cycles[index] is expected_cycle

    assert [cycle.cycle_number for cycle in cycle_history.cycles] == list(
        range(11)
    )