from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_case():
    return type(
        "Case",
        (),
        {
            "case_id": "case-summary-decision-integration-001",
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()


def build_workflow():
    return TechnicianWorkflow(build_case())


def build_summary():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)
    return workflow, summary


def build_recommendation(
    recommendation_type="TEST_RECOMMENDATION",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure requires technician review.",
    )


def build_decision(
    workflow,
    recommendation=None,
    decision_type=TechnicianDecisionType.ACCEPT,
    notes="Technician decision recorded.",
):
    if recommendation is None:
        recommendation = build_recommendation()

    return TechnicianDecision(
        workflow=workflow,
        recommendation=recommendation,
        decision_type=decision_type,
        notes=notes,
    )


def build_reasoning_summary(workflow):
    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )
    return cycle_history, reasoning


def complete_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_summary_exposes_original_case():
    workflow, summary = build_summary()

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id


def test_summary_exposes_original_workflow():
    workflow, summary = build_summary()

    assert summary.workflow is workflow
    assert summary.workflow_id == workflow.workflow_id


def test_summary_exposes_case_evidence_collections():
    workflow, summary = build_summary()

    assert summary.findings == workflow.case.findings
    assert summary.root_causes == workflow.case.root_causes
    assert summary.recommendations == workflow.case.recommendations


def test_summary_decision_is_separate_from_case_evidence():
    workflow, summary = build_summary()
    recommendation = build_recommendation()
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.recommendations == []
    assert summary.findings == []
    assert summary.root_causes == []


def test_summary_reasoning_is_separate_from_decision():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    assert summary.reasoning_summary is reasoning
    assert summary.decision is decision
    assert summary.reasoning_summary is not summary.decision


def test_decision_references_same_recommendation_object():
    workflow, summary = build_summary()
    recommendation = build_recommendation()
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    summary.set_decision(decision)

    assert summary.decision.recommendation is recommendation


def test_decision_references_same_workflow_as_summary():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision.workflow is workflow
    assert summary.decision.workflow is summary.workflow


def test_reasoning_references_same_workflow_as_summary():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)

    summary.set_reasoning_summary(reasoning)

    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.workflow is summary.workflow


def test_workflow_state_is_exposed_live_by_summary():
    workflow, summary = build_summary()

    assert summary.workflow_state is WorkflowState.OPEN

    workflow.start_investigation()

    assert summary.workflow_state is WorkflowState.INVESTIGATING


def test_decision_does_not_change_workflow_state():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert summary.workflow_state is WorkflowState.OPEN
    assert workflow.history == []


def test_decision_does_not_change_reasoning_overview():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)

    summary.set_reasoning_summary(reasoning)
    before = reasoning.overview

    summary.set_decision(build_decision(workflow))

    after = reasoning.overview

    assert after == before


def test_replacing_decision_does_not_change_case_evidence():
    workflow, summary = build_summary()

    first = build_decision(
        workflow,
        notes="First decision.",
    )
    second = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
        notes="Second decision.",
    )

    summary.set_decision(first)

    evidence_before = (
        summary.findings,
        summary.root_causes,
        summary.recommendations,
    )

    summary.set_decision(second)

    evidence_after = (
        summary.findings,
        summary.root_causes,
        summary.recommendations,
    )

    assert evidence_after == evidence_before


def test_replacing_reasoning_does_not_change_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    _, first_reasoning = build_reasoning_summary(workflow)
    _, second_reasoning = build_reasoning_summary(workflow)

    summary.set_decision(decision)
    summary.set_reasoning_summary(first_reasoning)
    summary.set_reasoning_summary(second_reasoning)

    assert summary.decision is decision
    assert summary.reasoning_summary is second_reasoning


def test_decision_and_reasoning_can_coexist():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    assert summary.reasoning_summary is reasoning
    assert summary.decision is decision
    assert summary.workflow is workflow


def test_terminal_workflow_preserves_complete_summary():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    complete_workflow(workflow)

    assert summary.is_terminal
    assert summary.workflow_state is WorkflowState.RESOLVED
    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning
    assert summary.workflow is workflow


def test_reopened_workflow_preserves_complete_summary():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert not summary.is_terminal
    assert summary.workflow_state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning


def test_summary_identity_remains_stable_through_lifecycle():
    workflow, summary = build_summary()
    summary_id = id(summary)

    summary.set_decision(build_decision(workflow))

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()
    workflow.reopen()

    assert id(summary) == summary_id
    assert summary.workflow is workflow


def test_decision_does_not_create_recovery_cycles():
    workflow, summary = build_summary()
    cycle_history = TechnicianRecoveryCycleHistory(workflow)

    summary.set_decision(build_decision(workflow))

    assert cycle_history.cycle_count == 1
    assert cycle_history.latest_cycle.is_original


def test_reasoning_and_decision_share_workflow_but_not_identity():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    assert reasoning.workflow is decision.workflow
    assert reasoning is not decision


def test_summary_remains_consistent_after_workflow_progression():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert summary.workflow is workflow
    assert summary.workflow_state is WorkflowState.ACTION_REQUIRED
    assert summary.decision.workflow is workflow
    assert summary.reasoning_summary.workflow is workflow


def test_summary_remains_consistent_after_resolution_and_reopen():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    complete_workflow(workflow)

    assert summary.workflow_state is WorkflowState.RESOLVED
    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning

    workflow.reopen()

    assert summary.workflow_state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning


def test_case_summary_does_not_duplicate_decision_data_into_reasoning():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    overview = summary.reasoning_summary.overview

    assert "decision" not in overview
    assert "decision_id" not in overview
    assert "decision_type" not in overview
    assert "decision_notes" not in overview


def test_case_summary_preserves_separation_of_responsibilities():
    workflow, summary = build_summary()
    _, reasoning = build_reasoning_summary(workflow)
    decision = build_decision(workflow)

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    assert summary.workflow is workflow
    assert summary.reasoning_summary is reasoning
    assert summary.decision is decision
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    workflow.start_investigation()

    assert summary.workflow_state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning


def test_full_case_summary_integration_survives_complete_lifecycle():
    workflow, summary = build_summary()
    recommendation = build_recommendation()
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Proceed with technician-approved recommendation.",
    )
    cycle_history, reasoning = build_reasoning_summary(workflow)

    summary.set_decision(decision)
    summary.set_reasoning_summary(reasoning)

    complete_workflow(workflow)

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_state is WorkflowState.RESOLVED
    assert summary.is_terminal

    assert summary.decision is decision
    assert summary.decision.workflow is workflow
    assert summary.decision.recommendation is recommendation
    assert summary.decision.decision_type is TechnicianDecisionType.ACCEPT

    assert summary.reasoning_summary is reasoning
    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.cycle_history is cycle_history

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []