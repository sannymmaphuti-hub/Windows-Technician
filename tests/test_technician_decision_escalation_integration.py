import pytest

from engine.diagnostic_case import DiagnosticCase
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


@pytest.fixture
def case():
    return DiagnosticCase()


@pytest.fixture
def workflow(case):
    return TechnicianWorkflow(case)


@pytest.fixture
def recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure may affect system responsiveness.",
    )


@pytest.fixture
def summary(workflow):
    return TechnicianCaseSummary(workflow)


def create_decision(workflow, recommendation, decision_type):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=recommendation,
        decision_type=decision_type,
        notes="Technician decision recorded for escalation boundary testing.",
    )


@pytest.mark.parametrize(
    "decision_type",
    TechnicianDecisionType,
)
def test_decision_does_not_automatically_escalate_workflow(
    summary,
    workflow,
    recommendation,
    decision_type,
):
    decision = create_decision(
        workflow,
        recommendation,
        decision_type,
    )

    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert not workflow.is_terminal


def test_escalate_decision_is_not_workflow_escalation(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.decision.decision_type is TechnicianDecisionType.ESCALATE
    assert workflow.state is WorkflowState.OPEN
    assert workflow.state is not WorkflowState.ESCALATED


def test_workflow_escalation_requires_explicit_workflow_transition(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert workflow.is_terminal


def test_explicit_workflow_escalation_does_not_create_decision(
    summary,
    workflow,
):
    workflow.escalate()

    assert summary.decision is None


def test_explicit_workflow_escalation_does_not_create_escalation_status(
    summary,
    workflow,
):
    workflow.escalate()

    assert summary.escalation_status is None


def test_escalation_status_can_be_recorded_independently(
    summary,
):
    summary.set_escalation_status("ESCALATED")

    assert summary.escalation_status == "ESCALATED"


def test_decision_does_not_automatically_create_escalation_status(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert summary.escalation_status is None


@pytest.mark.parametrize(
    "decision_type",
    [
        TechnicianDecisionType.ACCEPT,
        TechnicianDecisionType.REJECT,
        TechnicianDecisionType.DEFER,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    ],
)
def test_non_escalate_decisions_do_not_escalate(
    summary,
    workflow,
    recommendation,
    decision_type,
):
    decision = create_decision(
        workflow,
        recommendation,
        decision_type,
    )

    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert summary.escalation_status is None


def test_escalation_status_does_not_mutate_decision(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    summary.set_decision(decision)

    decision_id = decision.decision_id
    decision_type = decision.decision_type
    notes = decision.notes

    summary.set_escalation_status("ESCALATED")

    assert summary.decision.decision_id == decision_id
    assert summary.decision.decision_type is decision_type
    assert summary.decision.notes == notes


def test_workflow_escalation_does_not_mutate_decision(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    decision_id = decision.decision_id
    created_at = decision.created_at

    workflow.escalate()

    assert summary.decision is decision
    assert summary.decision.decision_id == decision_id
    assert summary.decision.created_at == created_at
    assert summary.decision.decision_type is TechnicianDecisionType.ESCALATE


def test_escalation_creates_workflow_history_only(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert workflow.history == []

    workflow.escalate()

    assert len(workflow.history) == 1
    assert workflow.history[0] == (
        WorkflowState.OPEN,
        WorkflowState.ESCALATED,
    )


def test_decision_does_not_create_workflow_history(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    assert workflow.history == []


def test_replacing_decision_does_not_change_escalation_state(
    summary,
    workflow,
    recommendation,
):
    first_decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    second_decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(first_decision)

    workflow.escalate()

    summary.set_decision(second_decision)

    assert workflow.state is WorkflowState.ESCALATED
    assert summary.decision is second_decision


def test_escalation_status_does_not_change_workflow_state(
    summary,
    workflow,
):
    summary.set_escalation_status("ESCALATED")

    assert workflow.state is WorkflowState.OPEN


def test_workflow_escalation_does_not_change_verification_status(
    summary,
    workflow,
):
    summary.set_verification_status("PENDING")

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert summary.verification_status == "PENDING"


def test_workflow_escalation_does_not_create_remediation_action(
    summary,
    workflow,
):
    workflow.escalate()

    assert summary.decision is None
    assert summary.remediation_status is None


def test_decision_and_escalation_remain_separate_concerns(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)
    summary.set_escalation_status("ESCALATED")

    assert summary.decision is decision
    assert summary.escalation_status == "ESCALATED"
    assert workflow.state is WorkflowState.OPEN


def test_full_escalation_boundary_preserves_decision_identity(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)
    summary.set_escalation_status("ESCALATED")

    decision_id = decision.decision_id
    created_at = decision.created_at

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert summary.escalation_status == "ESCALATED"
    assert summary.decision.decision_id == decision_id
    assert summary.decision.created_at == created_at


def test_escalated_workflow_is_terminal_but_decision_remains_available(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary.set_decision(decision)

    workflow.escalate()

    assert workflow.is_terminal
    assert summary.is_terminal
    assert summary.decision is decision