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

    return summary, case


def test_overview_is_new_dictionary():
    summary, _ = create_summary()

    overview = summary.overview

    assert overview is not summary.__dict__


def test_overview_findings_is_copy():
    summary, case = create_summary()

    overview = summary.overview

    assert overview["findings"] is not case.findings


def test_overview_correlations_is_copy():
    summary, case = create_summary()

    overview = summary.overview

    assert overview["correlations"] is not case.correlations


def test_overview_root_causes_is_copy():
    summary, case = create_summary()

    overview = summary.overview

    assert overview["root_causes"] is not case.root_causes


def test_overview_recommendations_is_copy():
    summary, case = create_summary()

    overview = summary.overview

    assert overview["recommendations"] is not case.recommendations


def test_overview_findings_mutation_is_safe():
    summary, case = create_summary()

    overview = summary.overview
    original_count = len(case.findings)

    overview["findings"].append("fake-finding")

    assert len(case.findings) == original_count


def test_overview_root_causes_mutation_is_safe():
    summary, case = create_summary()

    overview = summary.overview
    original_count = len(case.root_causes)

    overview["root_causes"].append("fake-root-cause")

    assert len(case.root_causes) == original_count


def test_overview_recommendations_mutation_is_safe():
    summary, case = create_summary()

    overview = summary.overview
    original_count = len(case.recommendations)

    overview["recommendations"].append("fake-recommendation")

    assert len(case.recommendations) == original_count