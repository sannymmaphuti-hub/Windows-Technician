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


def test_summary_reads_current_findings():
    summary, case = create_summary()

    case.findings.append("new-finding")

    assert summary.findings == ["new-finding"]
    assert summary.finding_count == 1


def test_summary_reads_current_correlations():
    summary, case = create_summary()

    case.correlations.append("new-correlation")

    assert summary.correlations == ["new-correlation"]
    assert summary.correlation_count == 1


def test_summary_reads_current_root_causes():
    summary, case = create_summary()

    case.root_causes.append("new-root-cause")

    assert summary.root_causes == ["new-root-cause"]
    assert summary.root_cause_count == 1


def test_summary_reads_current_recommendations():
    summary, case = create_summary()

    case.recommendations.append("new-recommendation")

    assert summary.recommendations == ["new-recommendation"]
    assert summary.recommendation_count == 1


def test_overview_reads_current_case_state():
    summary, case = create_summary()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    overview = summary.overview

    assert overview["finding_count"] == 1
    assert overview["correlation_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["recommendation_count"] == 1

    assert overview["findings"] == ["finding"]
    assert overview["correlations"] == ["correlation"]
    assert overview["root_causes"] == ["root-cause"]
    assert overview["recommendations"] == ["recommendation"]