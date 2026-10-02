import pytest

from engine.recommendation import Recommendation
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def workflow():
    return TechnicianWorkflow(FakeCase())


@pytest.fixture
def recommendation():
    return Recommendation(
        "memory_review",
        "MEMORY",
        "HIGH",
        "Review memory-intensive processes and close unnecessary applications.",
        "High memory usage may affect system responsiveness.",
    )


@pytest.fixture
def decision(workflow, recommendation):
    return TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        "Technician reviewed the recommendation.",
    )


def test_decision_requires_workflow(recommendation):
    with pytest.raises(ValueError):
        TechnicianDecision(
            None,
            recommendation,
            TechnicianDecisionType.ACCEPT,
        )


def test_decision_requires_recommendation(workflow):
    with pytest.raises(ValueError):
        TechnicianDecision(
            workflow,
            None,
            TechnicianDecisionType.ACCEPT,
        )


def test_decision_requires_valid_decision_type(workflow, recommendation):
    with pytest.raises(ValueError):
        TechnicianDecision(
            workflow,
            recommendation,
            "ACCEPT",
        )


def test_decision_has_unique_id(workflow, recommendation):
    first = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    second = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    assert first.decision_id != second.decision_id


def test_decision_has_utc_timestamp(decision):
    assert decision.created_at.tzinfo is not None
    assert decision.created_at.utcoffset().total_seconds() == 0


@pytest.mark.parametrize(
    "decision_type",
    [
        TechnicianDecisionType.ACCEPT,
        TechnicianDecisionType.REJECT,
        TechnicianDecisionType.DEFER,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        TechnicianDecisionType.ESCALATE,
    ],
)
def test_decision_accepts_all_valid_decision_types(
    workflow,
    recommendation,
    decision_type,
):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        decision_type,
    )

    assert decision.decision_type is decision_type


def test_decision_exposes_recommendation(decision, recommendation):
    assert decision.recommendation is recommendation


def test_decision_preserves_notes(workflow, recommendation):
    notes = "Reviewed memory evidence and confirmed technician action."

    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        notes,
    )

    assert decision.notes == notes


def test_notes_are_optional(workflow, recommendation):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.DEFER,
    )

    assert decision.notes == ""


def test_decision_is_immutable(decision):
    with pytest.raises((AttributeError, ValueError)):
        decision.decision_type = TechnicianDecisionType.REJECT

    with pytest.raises((AttributeError, ValueError)):
        decision.notes = "Changed decision."


def test_decision_does_not_mutate_workflow(workflow, recommendation):
    initial_state = workflow.state

    TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    assert workflow.state is initial_state


def test_decision_does_not_mutate_recommendation(recommendation, workflow):
    original_priority = recommendation.priority
    original_description = recommendation.description

    TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    assert recommendation.priority == original_priority
    assert recommendation.description == original_description


def test_recording_decision_does_not_execute_remediation(
    workflow,
    recommendation,
):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    assert not hasattr(decision, "execute")
    assert not hasattr(workflow, "execute_remediation")


def test_decision_identity_is_stable(decision):
    decision_id = decision.decision_id

    assert decision.decision_id == decision_id
    assert decision.decision_id == decision_id