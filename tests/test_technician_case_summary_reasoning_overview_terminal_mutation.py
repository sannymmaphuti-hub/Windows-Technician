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


def test_mutating_terminal_findings_does_not_mutate_case():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview
    overview["findings"].append("injected")

    assert case.findings == ["finding"]
    assert case_summary.reasoning_summary.findings == [
        "finding"
    ]


def test_mutating_terminal_root_causes_does_not_mutate_case():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.root_causes.append("root-cause")
    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview
    overview["root_causes"].append("injected")

    assert case.root_causes == ["root-cause"]
    assert case_summary.reasoning_summary.root_causes == [
        "root-cause"
    ]


def test_mutating_terminal_recommendations_does_not_mutate_case():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.recommendations.append("recommendation")
    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview
    overview["recommendations"].append("injected")

    assert case.recommendations == ["recommendation"]
    assert (
        case_summary.reasoning_summary.recommendations
        == ["recommendation"]
    )


def test_terminal_overview_repeated_reads_remain_isolated():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    first = case_summary.reasoning_summary.overview
    second = case_summary.reasoning_summary.overview

    assert first is not second
    assert first["findings"] is not second["findings"]
    assert first["root_causes"] is not second["root_causes"]
    assert (
        first["recommendations"]
        is not second["recommendations"]
    )

    first["findings"].clear()
    first["root_causes"].clear()
    first["recommendations"].clear()

    fresh = case_summary.reasoning_summary.overview

    assert fresh["findings"] == ["finding"]
    assert fresh["root_causes"] == ["root-cause"]
    assert fresh["recommendations"] == ["recommendation"]