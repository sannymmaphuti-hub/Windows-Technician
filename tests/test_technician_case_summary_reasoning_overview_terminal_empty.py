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

    history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(workflow)
    case_summary.set_reasoning_summary(reasoning_summary)

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    )


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_resolved_empty_overview_is_explicit():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert overview == {
        "finding_count": 0,
        "correlation_count": 0,
        "root_cause_count": 0,
        "recommendation_count": 0,
        "findings": [],
        "correlations": [],
        "root_causes": [],
        "recommendations": [],
    }


def test_resolved_empty_overview_contains_no_none_values():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert all(
        value is not None
        for value in overview.values()
    )


def test_resolved_empty_collections_are_isolated():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    first = case_summary.reasoning_summary.overview
    second = reasoning_summary.overview

    assert first["findings"] is not second["findings"]
    assert first["correlations"] is not second["correlations"]
    assert first["root_causes"] is not second["root_causes"]
    assert (
        first["recommendations"]
        is not second["recommendations"]
    )


def test_resolved_empty_overview_is_stable_across_reads():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    first = case_summary.reasoning_summary.overview
    second = case_summary.reasoning_summary.overview
    third = case_summary.reasoning_summary.overview

    assert first == second == third


def test_resolution_does_not_create_reasoning_evidence():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        _,
    ) = create_summaries()

    resolve_workflow(workflow)

    assert case.findings == []
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []

    assert reasoning_summary.findings == []
    assert reasoning_summary.correlations == []
    assert reasoning_summary.root_causes == []
    assert reasoning_summary.recommendations == []


def test_resolution_does_not_add_workflow_state_to_overview():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert workflow.state.name == "RESOLVED"
    assert "workflow_state" not in overview
    assert "state" not in overview
    assert "is_terminal" not in overview


def test_recovery_history_does_not_pollute_empty_overview():
    (
        _,
        workflow,
        history,
        _,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    overview = case_summary.reasoning_summary.overview

    assert history.cycle_count == 2
    assert overview["finding_count"] == 0
    assert overview["correlation_count"] == 0
    assert overview["root_cause_count"] == 0
    assert overview["recommendation_count"] == 0


def test_recovery_cycles_do_not_create_reasoning_evidence():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        _,
    ) = create_summaries()

    workflow.start_investigation()

    cycle_one = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_one)

    cycle_two = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(cycle_two)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert history.cycle_count == 3

    assert case.findings == []
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []

    assert reasoning_summary.overview[
        "finding_count"
    ] == 0


def test_terminal_empty_overview_remains_isolated_after_mutation():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    overview["findings"].append("injected")
    overview["correlations"].append("injected")
    overview["root_causes"].append("injected")
    overview["recommendations"].append("injected")

    fresh = case_summary.reasoning_summary.overview

    assert fresh["findings"] == []
    assert fresh["correlations"] == []
    assert fresh["root_causes"] == []
    assert fresh["recommendations"] == []

    assert fresh["finding_count"] == 0
    assert fresh["correlation_count"] == 0
    assert fresh["root_cause_count"] == 0
    assert fresh["recommendation_count"] == 0


def test_case_summary_and_reasoning_summary_share_same_empty_truth():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    assert case_summary.is_terminal is True

    assert (
        case_summary.reasoning_summary
        is reasoning_summary
    )

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    assert reasoning_summary.overview[
        "findings"
    ] == []

    assert reasoning_summary.overview[
        "correlations"
    ] == []

    assert reasoning_summary.overview[
        "root_causes"
    ] == []

    assert reasoning_summary.overview[
        "recommendations"
    ] == []