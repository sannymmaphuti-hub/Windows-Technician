from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    case = DiagnosticCase()
    return TechnicianWorkflow(case)


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(
    workflow,
    technician="Sanny",
    reason="Issue resolved",
):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason=reason,
    )


def build_reasoning_summary(workflow):
    cycle_history = TechnicianRecoveryCycleHistory(workflow)

    return TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )


def test_reasoning_summary_has_no_closure():
    workflow = build_workflow()

    reasoning_summary = build_reasoning_summary(workflow)

    assert not hasattr(reasoning_summary, "closure")


def test_creating_closure_does_not_modify_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    closure = build_closure(workflow)

    assert not hasattr(reasoning_summary, "closure")
    assert closure.workflow is workflow


def test_closure_does_not_become_reasoning_evidence():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    assert closure not in reasoning_summary.findings
    assert closure not in reasoning_summary.correlations
    assert closure not in reasoning_summary.root_causes
    assert closure not in reasoning_summary.recommendations


def test_closure_does_not_change_reasoning_counts():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    counts_before = (
        reasoning_summary.finding_count,
        reasoning_summary.correlation_count,
        reasoning_summary.root_cause_count,
        reasoning_summary.recommendation_count,
    )

    build_closure(workflow)

    counts_after = (
        reasoning_summary.finding_count,
        reasoning_summary.correlation_count,
        reasoning_summary.root_cause_count,
        reasoning_summary.recommendation_count,
    )

    assert counts_after == counts_before


def test_closure_does_not_change_reasoning_overview():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    overview_before = reasoning_summary.overview

    build_closure(workflow)

    overview_after = reasoning_summary.overview

    assert overview_after == overview_before


def test_reasoning_summary_and_closure_have_separate_identity():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    assert reasoning_summary is not closure


def test_reasoning_summary_does_not_create_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    assert not hasattr(reasoning_summary, "closure")


def test_closure_does_not_create_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert not hasattr(closure, "reasoning_summary")


def test_closure_metadata_is_independent_of_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    closure = build_closure(
        workflow,
        technician="Sanny",
        reason="Resolved after verification.",
    )

    assert closure.technician == "Sanny"
    assert closure.reason == "Resolved after verification."

    assert reasoning_summary.workflow is workflow
    assert closure.workflow is workflow


def test_reopening_workflow_does_not_mutate_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    overview_before = reasoning_summary.overview

    workflow.reopen()

    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.overview == overview_before
    assert closure.workflow is workflow


def test_closure_remains_valid_record_after_reopening():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    closure_id = closure.closure_id
    technician = closure.technician
    reason = closure.reason
    closure_state = closure.workflow_state

    workflow.reopen()

    assert closure.closure_id == closure_id
    assert closure.technician == technician
    assert closure.reason == reason
    assert closure.workflow_state is closure_state

    assert reasoning_summary.workflow is workflow


def test_reasoning_summary_binds_to_exact_workflow():
    workflow = build_workflow()

    reasoning_summary = build_reasoning_summary(workflow)

    assert reasoning_summary.workflow is workflow


def test_closure_binds_to_exact_workflow():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.workflow is workflow


def test_closure_does_not_replace_reasoning_evidence():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    findings_before = list(reasoning_summary.findings)
    correlations_before = list(reasoning_summary.correlations)
    root_causes_before = list(reasoning_summary.root_causes)
    recommendations_before = list(reasoning_summary.recommendations)

    build_closure(workflow)

    assert reasoning_summary.findings == findings_before
    assert reasoning_summary.correlations == correlations_before
    assert reasoning_summary.root_causes == root_causes_before
    assert reasoning_summary.recommendations == recommendations_before


def test_multiple_closures_do_not_accumulate_in_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)

    first = build_closure(
        workflow,
        technician="Sanny",
        reason="First closure.",
    )

    second = build_closure(
        workflow,
        technician="Technician 2",
        reason="Second closure.",
    )

    assert first is not second
    assert first not in reasoning_summary.findings
    assert second not in reasoning_summary.findings
    assert first not in reasoning_summary.root_causes
    assert second not in reasoning_summary.root_causes
    assert first not in reasoning_summary.recommendations
    assert second not in reasoning_summary.recommendations


def test_reasoning_summary_remains_independent_when_closure_exists():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.cycle_history is not None
    assert closure.workflow is workflow
    assert reasoning_summary is not closure