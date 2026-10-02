from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
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


def enter_investigation(workflow):
    workflow.start_investigation()


def complete_workflow(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_case_summary_recovery_history_starts_with_original_cycle():
    (
        _,
        _,
        history,
        _,
        summary,
    ) = create_summary()

    assert history.cycle_count == 1
    assert history.latest_cycle.is_original is True
    assert history.latest_cycle.is_recovery is False

    assert summary.reasoning_summary.cycle_history is history


def test_recovery_cycle_creation_preserves_case_summary_identity():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        summary,
    ) = create_summary()

    case_id = summary.case_id
    workflow_id = summary.workflow_id

    enter_investigation(workflow)

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    assert history.cycle_count == 2

    assert summary.case_id == case_id
    assert summary.workflow_id == workflow_id

    assert reasoning_summary.case_id == case_id
    assert reasoning_summary.workflow_id == workflow_id


def test_multiple_recovery_cycles_remain_separate_from_reasoning():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    enter_investigation(workflow)

    cycle_one = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_one)

    cycle_two = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_two)

    assert history.cycle_count == 3

    overview = reasoning_summary.overview

    assert overview["finding_count"] == 1
    assert overview["root_cause_count"] == 1

    assert overview["findings"] == ["finding"]
    assert overview["root_causes"] == ["root-cause"]

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]


def test_recovery_cycle_history_is_not_exposed_as_reasoning_evidence():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        _,
    ) = create_summary()

    enter_investigation(workflow)

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    overview = reasoning_summary.overview

    assert "cycles" not in overview
    assert "cycle_history" not in overview
    assert "recovery_cycles" not in overview


def test_recovery_cycles_do_not_change_reasoning_counts():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        _,
    ) = create_summary()

    case.findings.extend(
        ["finding-1", "finding-2"]
    )
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    before = reasoning_summary.overview

    enter_investigation(workflow)

    cycle_one = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_one)

    cycle_two = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_two)

    after = reasoning_summary.overview

    assert after == before
    assert history.cycle_count == 3


def test_recovery_cycles_do_not_duplicate_case_evidence():
    (
        case,
        workflow,
        history,
        _,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    enter_investigation(workflow)

    for _ in range(3):
        cycle = history.latest_cycle.start_recovery_cycle()
        history.record_cycle(cycle)

    assert history.cycle_count == 4

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == [
        "recommendation"
    ]


def test_recovery_history_remains_available_after_resolution():
    (
        _,
        workflow,
        history,
        _,
        summary,
    ) = create_summary()

    enter_investigation(workflow)

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    complete_workflow(workflow)

    assert workflow.is_terminal is True
    assert history.cycle_count == 2
    assert summary.reasoning_summary.cycle_history is history


def test_recovery_history_remains_available_after_reopen():
    (
        _,
        workflow,
        history,
        _,
        summary,
    ) = create_summary()

    enter_investigation(workflow)

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    complete_workflow(workflow)

    workflow.reopen()

    assert workflow.is_terminal is False
    assert history.cycle_count == 2
    assert summary.reasoning_summary.cycle_history is history


def test_recovery_and_reasoning_remain_distinct_after_full_lifecycle():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        summary,
    ) = create_summary()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    enter_investigation(workflow)

    cycle_one = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_one)

    cycle_two = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_two)

    complete_workflow(workflow)
    workflow.reopen()

    overview = reasoning_summary.overview

    assert history.cycle_count == 3

    assert overview["finding_count"] == 1
    assert overview["correlation_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["recommendation_count"] == 1

    assert summary.reasoning_summary is reasoning_summary
    assert summary.reasoning_summary.cycle_history is history

    assert summary.findings == ["finding"]
    assert summary.root_causes == ["root-cause"]
    assert summary.recommendations == [
        "recommendation"
    ]