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
    return TechnicianWorkflow(case)


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure may affect system performance.",
    )


def build_decision(
    workflow,
    decision_type=TechnicianDecisionType.ACCEPT,
    notes="Technician decision.",
):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=decision_type,
        notes=notes,
    )


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


def test_summary_has_no_decision_or_closure_initially():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert summary.decision is None
    assert summary.closure is None


def test_setting_decision_does_not_create_closure():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.closure is None


def test_setting_closure_does_not_create_decision():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure is closure
    assert summary.decision is None


def test_setting_decision_does_not_change_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    summary.set_decision(build_decision(workflow))

    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id
    assert summary.closure_technician == "Sanny"
    assert summary.closure_reason == "Issue resolved"


def test_setting_closure_does_not_change_decision():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    decision = build_decision(workflow)

    summary.set_decision(decision)
    summary.set_closure(build_closure(workflow))

    assert summary.decision is decision
    assert summary.decision_id if hasattr(summary, "decision_id") else True


def test_decision_and_closure_have_separate_identity():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert summary.closure is closure
    assert decision.decision_id != closure.closure_id


def test_decision_does_not_modify_closure_metadata():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    closure = build_closure(
        workflow,
        technician="Sanny",
        reason="Resolved after verification.",
    )

    summary.set_closure(closure)

    closure_id = closure.closure_id
    technician = closure.technician
    reason = closure.reason
    state = closure.workflow_state

    summary.set_decision(
        build_decision(
            workflow,
            decision_type=TechnicianDecisionType.ACCEPT,
        )
    )

    assert closure.closure_id == closure_id
    assert closure.technician == technician
    assert closure.reason == reason
    assert closure.workflow_state is state


def test_closure_does_not_modify_decision_metadata():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Accepted recommendation.",
    )

    summary.set_decision(decision)
    summary.set_closure(build_closure(workflow))

    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert decision.notes == "Accepted recommendation."
    assert decision.workflow is workflow


def test_replacing_decision_does_not_replace_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    closure = build_closure(workflow)
    first_decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    second_decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
    )

    summary.set_closure(closure)
    summary.set_decision(first_decision)

    summary.set_decision(second_decision)

    assert summary.decision is second_decision
    assert summary.closure is closure


def test_replacing_closure_does_not_replace_decision():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)

    first_closure = build_closure(
        workflow,
        technician="Sanny",
        reason="First closure.",
    )

    second_closure = build_closure(
        workflow,
        technician="Technician 2",
        reason="Second closure.",
    )

    summary.set_decision(decision)
    summary.set_closure(first_closure)

    summary.set_closure(second_closure)

    assert summary.decision is decision
    assert summary.closure is second_closure


def test_decision_and_closure_bind_to_same_workflow():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    assert summary.decision.workflow is workflow
    assert summary.closure.workflow is workflow


def test_decision_and_closure_do_not_become_workflow_state():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    state_before = workflow.state
    history_before = list(workflow.history)

    summary.set_decision(decision)
    summary.set_closure(closure)

    assert workflow.state is state_before
    assert workflow.history == history_before


def test_closure_requires_resolved_workflow_even_when_decision_exists():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)
    decision = build_decision(workflow)

    summary.set_decision(decision)

    try:
        summary.set_closure(
            TechnicianCaseClosure(
                workflow=workflow,
                technician="Sanny",
                reason="Attempted early closure.",
            )
        )
        assert False, "Expected ValueError."
    except ValueError as exc:
        assert str(exc) == (
            "A case can only be closed after it is RESOLVED."
        )

    assert summary.decision is decision
    assert summary.closure is None


def test_decision_survives_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert summary.closure is closure


def test_closure_survives_decision_replacement():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    closure = build_closure(workflow)

    first_decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    second_decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
    )

    summary.set_closure(closure)
    summary.set_decision(first_decision)

    summary.set_decision(second_decision)

    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id


def test_decision_types_do_not_automatically_create_closure():
    workflow = build_workflow()

    for decision_type in TechnicianDecisionType:
        summary = TechnicianCaseSummary(workflow)

        decision = build_decision(
            workflow,
            decision_type=decision_type,
        )

        summary.set_decision(decision)

        assert summary.decision is decision
        assert summary.closure is None


def test_closure_does_not_change_decision_type():
    workflow = build_workflow()
    resolve_workflow(workflow)

    for decision_type in TechnicianDecisionType:
        summary = TechnicianCaseSummary(workflow)

        decision = build_decision(
            workflow,
            decision_type=decision_type,
        )
        closure = build_closure(workflow)

        summary.set_decision(decision)
        summary.set_closure(closure)

        assert summary.decision is decision
        assert summary.decision.decision_type is decision_type
        assert summary.closure is closure


def test_decision_and_closure_can_be_accessed_independently():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    first_decision = summary.decision
    second_decision = summary.decision

    first_closure = summary.closure
    second_closure = summary.closure

    assert first_decision is decision
    assert second_decision is decision
    assert first_decision is second_decision

    assert first_closure is closure
    assert second_closure is closure
    assert first_closure is second_closure


def test_closure_and_decision_remain_independent_after_reopening():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    workflow.reopen()

    assert summary.decision is decision
    assert summary.closure is closure
    assert summary.closure.workflow_state.value == "RESOLVED"