from engine.diagnostic_case import DiagnosticCase
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
    return TechnicianReasoningSummary(
        workflow,
        history,
    )


def reasoning_snapshot(summary):
    return {
        "finding_count": summary.finding_count,
        "correlation_count": summary.correlation_count,
        "root_cause_count": summary.root_cause_count,
        "recommendation_count": summary.recommendation_count,
        "findings": summary.findings,
        "correlations": summary.correlations,
        "root_causes": summary.root_causes,
        "recommendations": summary.recommendations,
    }


def test_reasoning_summary_uses_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    summary = build_summary(workflow, history)

    assert summary.cycle_history is history


def test_reasoning_summary_and_recovery_history_share_workflow():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    assert history.workflow is workflow
    assert summary.workflow is workflow


def test_initial_recovery_history_contains_cycle_zero():
    workflow = build_workflow()
    history = build_history(workflow)

    assert history.cycle_count == 1
    assert history.latest_cycle.cycle_number == 0


def test_adding_recovery_cycle_updates_history_count():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert history.cycle_count == 2
    assert summary.cycle_history.cycle_count == 2


def test_adding_recovery_cycle_updates_latest_cycle():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.cycle_history.latest_cycle is cycle


def test_recovery_cycle_does_not_change_reasoning_counts():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    before = reasoning_snapshot(summary)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert reasoning_snapshot(summary) == before


def test_recovery_cycle_does_not_create_findings():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.findings == []


def test_recovery_cycle_does_not_create_correlations():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.correlations == []


def test_recovery_cycle_does_not_create_root_causes():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.root_causes == []


def test_recovery_cycle_does_not_create_recommendations():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.recommendations == []


def test_multiple_recovery_cycles_remain_visible_through_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )
    third = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    history.record_cycle(second)
    history.record_cycle(third)

    assert [
        cycle.cycle_number
        for cycle in summary.cycle_history.cycles
    ] == [0, 1, 2]


def test_recovery_history_preserves_summary_workflow_identity():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.workflow is workflow
    assert summary.workflow.workflow_id == workflow.workflow_id
    assert summary.cycle_history.workflow is workflow


def test_recovery_cycle_does_not_change_workflow_state():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    state_before = workflow.state

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert workflow.state is state_before
    assert summary.workflow.state is state_before


def test_recovery_cycle_does_not_change_workflow_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    history_before = list(workflow.history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert workflow.history == history_before
    assert summary.workflow.history == history_before

def test_reasoning_overview_does_not_contain_recovery_cycle_as_evidence():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    overview = summary.overview

    assert cycle not in overview.get("findings", [])
    assert cycle not in overview.get("correlations", [])
    assert cycle not in overview.get("root_causes", [])
    assert cycle not in overview.get("recommendations", [])


def test_recovery_cycle_history_and_reasoning_summary_have_separate_roles():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.cycle_history is history
    assert cycle in history.cycles
    assert cycle not in summary.findings
    assert cycle not in summary.correlations
    assert cycle not in summary.root_causes
    assert cycle not in summary.recommendations