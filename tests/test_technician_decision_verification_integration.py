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
        notes="Technician decision recorded for verification boundary testing.",
    )


def test_verification_status_is_initially_none(summary):
    assert summary.verification_status is None


def test_verification_status_can_be_recorded_independently(summary):
    verification = "VERIFIED"

    summary.set_verification_status(verification)

    assert summary.verification_status == verification


def test_decision_can_exist_before_verification(
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

    assert summary.decision is decision
    assert summary.verification_status is None


def test_verification_does_not_create_decision(
    summary,
):
    summary.set_verification_status("VERIFIED")

    assert summary.decision is None


@pytest.mark.parametrize(
    "decision_type",
    TechnicianDecisionType,
)
def test_decision_type_does_not_determine_verification_status(
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
    summary.set_verification_status("VERIFIED")

    assert summary.decision is decision
    assert summary.decision.decision_type is decision_type
    assert summary.verification_status == "VERIFIED"


@pytest.mark.parametrize(
    "decision_type",
    TechnicianDecisionType,
)
def test_decision_does_not_automatically_create_verification_status(
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

    assert summary.verification_status is None


def test_accept_does_not_mean_verified(
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

    assert summary.decision.decision_type is TechnicianDecisionType.ACCEPT
    assert summary.verification_status is None


def test_reject_does_not_mean_verification_failed(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.REJECT,
    )

    summary.set_decision(decision)

    assert summary.decision.decision_type is TechnicianDecisionType.REJECT
    assert summary.verification_status is None


def test_defer_does_not_determine_verification(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.DEFER,
    )

    summary.set_decision(decision)
    summary.set_verification_status("PENDING")

    assert summary.decision.decision_type is TechnicianDecisionType.DEFER
    assert summary.verification_status == "PENDING"


def test_investigate_further_does_not_determine_verification(
    summary,
    workflow,
    recommendation,
):
    decision = create_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )

    summary.set_decision(decision)
    summary.set_verification_status("PENDING")

    assert (
        summary.decision.decision_type
        is TechnicianDecisionType.INVESTIGATE_FURTHER
    )
    assert summary.verification_status == "PENDING"


def test_escalate_decision_does_not_determine_verification(
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
    summary.set_verification_status("FAILED")

    assert summary.decision.decision_type is TechnicianDecisionType.ESCALATE
    assert summary.verification_status == "FAILED"


def test_verification_status_does_not_mutate_decision(
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

    original_id = decision.decision_id
    original_type = decision.decision_type
    original_notes = decision.notes

    summary.set_verification_status("VERIFIED")

    assert summary.decision.decision_id == original_id
    assert summary.decision.decision_type is original_type
    assert summary.decision.notes == original_notes


def test_verification_status_does_not_replace_recommendation(
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
    summary.set_verification_status("VERIFIED")

    assert summary.decision.recommendation is recommendation


def test_replacing_decision_does_not_change_existing_verification_status(
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
        TechnicianDecisionType.DEFER,
    )

    summary.set_decision(first_decision)
    summary.set_verification_status("VERIFIED")

    summary.set_decision(second_decision)

    assert summary.decision is second_decision
    assert summary.verification_status == "VERIFIED"


def test_verification_does_not_create_workflow_history(
    summary,
    workflow,
):
    history_before = workflow.history

    summary.set_verification_status("VERIFIED")

    assert workflow.history == history_before


def test_decision_and_verification_are_separate_summary_fields(
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
    summary.set_verification_status("VERIFIED")

    assert summary.decision is decision
    assert summary.verification_status == "VERIFIED"
    assert summary.decision is not summary.verification_status


def test_verification_status_survives_workflow_progression(
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
    summary.set_verification_status("VERIFIED")

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert summary.verification_status == "VERIFIED"
    assert summary.decision is decision


def test_decision_identity_survives_verification_and_resolution(
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
    summary.set_verification_status("VERIFIED")

    decision_id = decision.decision_id
    created_at = decision.created_at

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.decision.decision_id == decision_id
    assert summary.decision.created_at == created_at
    assert summary.verification_status == "VERIFIED"


def test_verification_can_change_without_mutating_decision(
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
    summary.set_verification_status("PENDING")

    decision_id = decision.decision_id

    summary.set_verification_status("VERIFIED")

    assert summary.verification_status == "VERIFIED"
    assert summary.decision.decision_id == decision_id
    assert summary.decision.decision_type is TechnicianDecisionType.ACCEPT


def test_failed_verification_does_not_change_decision(
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
    summary.set_verification_status("FAILED")

    assert summary.verification_status == "FAILED"
    assert summary.decision is decision
    assert summary.decision.decision_type is TechnicianDecisionType.ACCEPT