from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return workflow


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure may affect system performance.",
    )


def build_decision(workflow, decision_type=TechnicianDecisionType.ACCEPT):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=decision_type,
        notes="Technician decision recorded.",
    )


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Sanny",
        reason="Issue resolved",
    )


def test_decision_does_not_automatically_close_case():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None
    assert summary.closure_id is None


def test_decision_does_not_create_case_closure():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.closure is None


def test_decision_does_not_determine_closure_reason():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert summary.closure_reason == "Issue resolved"


def test_accept_decision_does_not_close_case():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None


def test_reject_decision_does_not_close_case():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None


def test_defer_decision_does_not_close_case():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None


def test_investigate_further_decision_does_not_close_case():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None


def test_escalate_decision_does_not_close_case():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert summary.closure is None


def test_explicit_closure_is_separate_from_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id
    assert summary.closure_technician == "Sanny"
    assert summary.closure_reason == "Issue resolved"


def test_closure_does_not_change_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    original_id = decision.decision_id
    original_type = decision.decision_type
    original_recommendation = decision.recommendation
    original_notes = decision.notes

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert decision.decision_id == original_id
    assert decision.decision_type is original_type
    assert decision.recommendation is original_recommendation
    assert decision.notes == original_notes


def test_closure_does_not_create_workflow_history():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)
    history_before_closure = list(workflow.history)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.history == history_before_closure


def test_closure_does_not_create_remediation_status():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.remediation_status is None

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.remediation_status is None


def test_closure_does_not_create_verification_status():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.verification_status is None

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.verification_status is None


def test_closure_does_not_create_escalation_status():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.escalation_status is None

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.escalation_status is None


def test_closure_requires_matching_workflow():
    workflow = build_workflow()
    other_workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    resolve_workflow(workflow)
    resolve_workflow(other_workflow)

    closure = build_closure(other_workflow)

    try:
        summary.set_closure(closure)
        assert False, "Expected ValueError for closure belonging to another workflow."
    except ValueError as exc:
        assert str(exc) == "Closure belongs to a different workflow."


def test_closure_rejects_invalid_object():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    try:
        summary.set_closure(object())
        assert False, "Expected ValueError for invalid closure."
    except ValueError as exc:
        assert str(exc) == "Case summary requires a TechnicianCaseClosure."


def test_decision_and_closure_have_separate_identity():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert decision.decision_id != closure.closure_id


def test_decision_survives_explicit_case_closure():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    original_decision_id = decision.decision_id
    original_created_at = decision.created_at

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.is_terminal
    assert workflow.state.value == "RESOLVED"
    assert summary.decision is decision
    assert decision.decision_id == original_decision_id
    assert decision.created_at == original_created_at
    assert summary.closure is closure


def test_replacing_closure_does_not_change_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    first_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Sanny",
        reason="First closure reason",
    )
    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Technician 2",
        reason="Updated closure reason",
    )

    summary.set_closure(first_closure)

    original_decision_id = decision.decision_id

    summary.set_closure(second_closure)

    assert summary.closure is second_closure
    assert summary.closure_id == second_closure.closure_id
    assert summary.closure_technician == "Technician 2"
    assert summary.closure_reason == "Updated closure reason"

    assert summary.decision is decision
    assert decision.decision_id == original_decision_id


def test_closure_does_not_become_case_evidence():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_closure_does_not_create_reasoning_summary():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.reasoning_summary is None

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.reasoning_summary is None


def test_decision_and_closure_remain_separate_after_full_case_lifecycle():
    workflow = build_workflow()
    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal

    assert summary.decision is decision
    assert summary.closure is closure

    assert summary.decision.decision_id != summary.closure.closure_id


def test_case_closure_is_explicit_after_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.closure is None

    resolve_workflow(workflow)

    assert summary.closure is None

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.closure is closure
    assert summary.closure_state == workflow.state


def test_decision_does_not_control_closure_reason():
    workflow = build_workflow()

    decision = TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=TechnicianDecisionType.REJECT,
        notes="Technician rejected the recommendation.",
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    resolve_workflow(workflow)

    closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Sanny",
        reason="Resolved after further investigation.",
    )

    summary.set_closure(closure)

    assert decision.decision_type is TechnicianDecisionType.REJECT
    assert summary.closure_reason == "Resolved after further investigation."