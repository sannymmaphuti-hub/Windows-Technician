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

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    )


def test_recovery_cycle_does_not_change_reasoning_overview():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    before = case_summary.reasoning_summary.overview

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    after = case_summary.reasoning_summary.overview

    assert history.cycle_count == 2
    assert after == before
    assert after == reasoning_summary.overview


def test_recovery_cycle_does_not_duplicate_case_evidence():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["findings"] == ["finding"]
    assert overview["root_causes"] == ["root-cause"]
    assert overview == reasoning_summary.overview


def test_multiple_recovery_cycles_do_not_change_reasoning_overview():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    cycle_one = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_one)

    cycle_two = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_two)

    overview = case_summary.reasoning_summary.overview

    assert history.cycle_count == 3
    assert overview == reasoning_summary.overview


def test_recovery_history_remains_separate_from_reasoning_overview():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    overview = case_summary.reasoning_summary.overview

    assert "cycle_history" not in overview
    assert "cycle_count" not in overview
    assert overview == reasoning_summary.overview