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

    return summary


def test_overview_calls_return_independent_findings():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    assert first["findings"] is not second["findings"]


def test_overview_calls_return_independent_correlations():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    assert first["correlations"] is not second["correlations"]


def test_overview_calls_return_independent_root_causes():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    assert first["root_causes"] is not second["root_causes"]


def test_overview_calls_return_independent_recommendations():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    assert (
        first["recommendations"]
        is not second["recommendations"]
    )


def test_mutating_first_overview_does_not_change_second():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    first["findings"].append("temporary")

    assert second["findings"] == []


def test_mutating_second_overview_does_not_change_first():
    summary = create_summary()

    first = summary.overview
    second = summary.overview

    second["recommendations"].append("temporary")

    assert first["recommendations"] == []