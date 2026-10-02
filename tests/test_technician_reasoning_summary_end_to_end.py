from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def test_reasoning_summary_end_to_end():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    history = TechnicianRecoveryCycleHistory(workflow)

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    original_case_id = case.case_id
    original_workflow_id = workflow.workflow_id

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.case_id == original_case_id
    assert summary.workflow_id == original_workflow_id

    assert summary.workflow is workflow
    assert summary.cycle_history is history

    assert summary.cycle_history.cycle_count == 2
    assert summary.cycle_history.latest_cycle is recovery_cycle
    assert summary.cycle_history.latest_cycle.outcome == "RESOLVED"

    assert summary.findings == []
    assert summary.correlations == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    assert summary.finding_count == 0
    assert summary.correlation_count == 0
    assert summary.root_cause_count == 0
    assert summary.recommendation_count == 0

    overview = summary.overview

    assert set(overview.keys()) == {
        "finding_count",
        "correlation_count",
        "root_cause_count",
        "recommendation_count",
        "findings",
        "correlations",
        "root_causes",
        "recommendations",
    }

    assert overview["finding_count"] == 0
    assert overview["correlation_count"] == 0
    assert overview["root_cause_count"] == 0
    assert overview["recommendation_count"] == 0