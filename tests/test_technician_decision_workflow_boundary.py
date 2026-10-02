from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


def build_workflow():
    case = type(
        "Case",
        (),
        {
            "case_id": "decision-workflow-boundary-001",
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()

    return TechnicianWorkflow(case)


def build_recommendation():
    return Recommendation(
        recommendation_type="TEST_RECOMMENDATION",
        category="TEST",
        priority="HIGH",
        description="Technician must review the recommendation.",
        rationale="The case requires technician judgment.",
    )


def build_decision(
    workflow,
    decision_type,
    notes="Technician decision recorded.",
):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=decision_type,
        notes=notes,
    )


def test_decision_does_not_change_workflow_state():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    assert decision.workflow is workflow
    assert workflow.state is WorkflowState.OPEN


def test_accept_decision_does_not_advance_workflow():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert workflow.state is WorkflowState.OPEN


def test_reject_decision_does_not_advance_workflow():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert workflow.state is WorkflowState.OPEN


def test_defer_decision_does_not_advance_workflow():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert workflow.state is WorkflowState.OPEN


def test_investigate_further_decision_does_not_advance_workflow():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert workflow.state is WorkflowState.OPEN


def test_escalate_decision_does_not_advance_workflow():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert workflow.state is WorkflowState.OPEN


def test_decision_does_not_create_workflow_history():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    before = workflow.history

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary.set_decision(decision)

    assert workflow.history == before
    assert workflow.history == []


def test_decision_does_not_change_terminal_status():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.is_terminal

    history_before = workflow.history

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary.set_decision(decision)

    assert workflow.is_terminal
    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.history == history_before


def test_decision_does_not_change_escalated_status():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()
    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert workflow.is_terminal

    history_before = workflow.history

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert workflow.state is WorkflowState.ESCALATED
    assert workflow.is_terminal
    assert workflow.history == history_before


def test_workflow_can_progress_independently_after_decision():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary.set_decision(decision)

    workflow.start_investigation()

    assert summary.decision is decision
    assert workflow.state is WorkflowState.INVESTIGATING


def test_decision_remains_bound_to_same_workflow_during_progression():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert decision.workflow is workflow
    assert summary.decision.workflow is workflow
    assert summary.workflow is workflow


def test_different_decision_types_are_distinct_records():
    workflow = build_workflow()

    decisions = [
        build_decision(
            workflow,
            TechnicianDecisionType.ACCEPT,
        ),
        build_decision(
            workflow,
            TechnicianDecisionType.REJECT,
        ),
        build_decision(
            workflow,
            TechnicianDecisionType.DEFER,
        ),
        build_decision(
            workflow,
            TechnicianDecisionType.INVESTIGATE_FURTHER,
        ),
        build_decision(
            workflow,
            TechnicianDecisionType.ESCALATE,
        ),
    ]

    decision_types = [
        decision.decision_type
        for decision in decisions
    ]

    decision_ids = [
        decision.decision_id
        for decision in decisions
    ]

    assert decision_types == [
        TechnicianDecisionType.ACCEPT,
        TechnicianDecisionType.REJECT,
        TechnicianDecisionType.DEFER,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        TechnicianDecisionType.ESCALATE,
    ]

    assert len(set(decision_ids)) == 5


def test_decision_records_do_not_mutate_each_other():
    workflow = build_workflow()

    accepted = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        notes="Accepted.",
    )

    rejected = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
        notes="Rejected.",
    )

    assert accepted.decision_type is TechnicianDecisionType.ACCEPT
    assert accepted.notes == "Accepted."

    assert rejected.decision_type is TechnicianDecisionType.REJECT
    assert rejected.notes == "Rejected."


def test_case_summary_replacement_changes_decision_not_workflow():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    accepted = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    escalated = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(accepted)

    assert summary.decision is accepted
    assert workflow.state is WorkflowState.OPEN

    summary.set_decision(escalated)

    assert summary.decision is escalated
    assert summary.decision.decision_type is (
        TechnicianDecisionType.ESCALATE
    )
    assert workflow.state is WorkflowState.OPEN


def test_decision_is_recorded_without_becoming_workflow_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.ESCALATE
    )

    assert summary.workflow_state is WorkflowState.OPEN
    assert summary.workflow_state is not summary.decision.decision_type