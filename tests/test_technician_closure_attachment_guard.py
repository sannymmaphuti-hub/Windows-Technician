import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(workflow, technician="Test Technician"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason="Issue resolved and verified.",
    )


def build_summary(workflow):
    return TechnicianCaseSummary(workflow)


def build_summary_with_state(workflow):
    summary = build_summary(workflow)

    recommendation = _build_recommendation()

    summary.set_decision(
        TechnicianDecision(
            workflow=workflow,
            recommendation=recommendation,
            decision_type=TechnicianDecisionType.ACCEPT,
            notes="Recommendation accepted.",
        )
    )

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician investigation note.")
    summary.set_notes(notes)

    summary.set_remediation_status("COMPLETED")
    summary.set_verification_status("VERIFIED")
    summary.set_escalation_status("NOT_ESCALATED")

    return summary


def _build_recommendation():
    from engine.recommendation import Recommendation

    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def summary_state_snapshot(summary):
    decision_id = (
        None
        if summary.decision is None
        else summary.decision.decision_id
    )

    return {
        "case_id": summary.case_id,
        "workflow_id": summary.workflow_id,
        "workflow_state": summary.workflow_state,
        "decision_id": decision_id,
        "notes": [
            (
                note.note_id,
                note.text,
                note.workflow_state,
            )
            for note in summary.notes
        ],
        "remediation_status": summary.remediation_status,
        "verification_status": summary.verification_status,
        "escalation_status": summary.escalation_status,
        "closure": summary.closure,
    }


def test_valid_closure_can_be_attached():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure is closure


def test_attached_closure_is_exposed_by_summary():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure_id == closure.closure_id
    assert summary.closure_technician == closure.technician
    assert summary.closure_reason == closure.reason
    assert summary.closure_state == closure.workflow_state


def test_invalid_none_closure_is_rejected():
    workflow = build_workflow()
    summary = build_summary(workflow)

    with pytest.raises(ValueError):
        summary.set_closure(None)

    assert summary.closure is None


def test_invalid_string_closure_is_rejected():
    workflow = build_workflow()
    summary = build_summary(workflow)

    with pytest.raises(ValueError):
        summary.set_closure("invalid closure")

    assert summary.closure is None


def test_invalid_object_closure_is_rejected():
    workflow = build_workflow()
    summary = build_summary(workflow)

    with pytest.raises(ValueError):
        summary.set_closure(object())

    assert summary.closure is None


def test_invalid_closure_does_not_change_summary_state():
    workflow = build_workflow()
    summary = build_summary_with_state(workflow)

    before = summary_state_snapshot(summary)

    with pytest.raises(ValueError):
        summary.set_closure(object())

    after = summary_state_snapshot(summary)

    assert after == before


def test_invalid_closure_does_not_change_workflow_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    state_before = workflow.state

    with pytest.raises(ValueError):
        summary.set_closure(object())

    assert workflow.state is state_before


def test_invalid_closure_does_not_change_workflow_history():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    history_before = list(workflow.history)

    with pytest.raises(ValueError):
        summary.set_closure(object())

    assert workflow.history == history_before


def test_cross_workflow_closure_is_rejected():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    foreign_closure = build_closure(
        workflow_b,
        technician="Other Technician",
    )

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert summary.closure is None


def test_cross_workflow_closure_does_not_change_summary_state():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary_with_state(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    foreign_closure = build_closure(workflow_b)

    before = summary_state_snapshot(summary)

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert summary_state_snapshot(summary) == before


def test_cross_workflow_closure_does_not_change_workflow_a():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    history_before = list(workflow_a.history)
    state_before = workflow_a.state

    foreign_closure = build_closure(workflow_b)

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert workflow_a.state is state_before
    assert workflow_a.history == history_before


def test_cross_workflow_closure_does_not_change_workflow_b():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    history_before = list(workflow_b.history)
    state_before = workflow_b.state

    foreign_closure = build_closure(workflow_b)

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert workflow_b.state is state_before
    assert workflow_b.history == history_before


def test_foreign_closure_is_not_attached_after_rejection():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    foreign_closure = build_closure(workflow_b)

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert summary.closure is None


def test_valid_closure_can_replace_existing_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    second_closure = build_closure(
        workflow,
        technician="Second Technician",
    )
    summary.set_closure(second_closure)

    assert summary.closure is second_closure
    assert summary.closure is not first_closure


def test_rejected_foreign_closure_does_not_replace_existing_closure():
    workflow_a = build_workflow()
    workflow_b = build_workflow()

    summary = build_summary(workflow_a)

    resolve_workflow(workflow_a)
    resolve_workflow(workflow_b)

    valid_closure = build_closure(workflow_a)
    summary.set_closure(valid_closure)

    foreign_closure = build_closure(
        workflow_b,
        technician="Foreign Technician",
    )

    with pytest.raises(ValueError):
        summary.set_closure(foreign_closure)

    assert summary.closure is valid_closure


def test_rejected_invalid_closure_preserves_existing_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    valid_closure = build_closure(workflow)
    summary.set_closure(valid_closure)

    with pytest.raises(ValueError):
        summary.set_closure(None)

    assert summary.closure is valid_closure


def test_valid_closure_requires_matching_workflow_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure.workflow is workflow

    summary.set_closure(closure)

    assert summary.closure.workflow is workflow