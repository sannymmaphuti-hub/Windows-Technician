from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
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


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure may affect system performance.",
    )


def build_decision(workflow):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Technician accepted the recommendation.",
    )


def build_reasoning_summary(workflow):
    cycle_history = TechnicianRecoveryCycleHistory(workflow)

    return TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )


def test_summary_has_no_closure_initially():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert summary.closure is None
    assert summary.closure_id is None
    assert summary.closure_technician is None
    assert summary.closure_reason is None
    assert summary.closure_state is None


def test_summary_exposes_exact_closure_identity():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id


def test_summary_exposes_closure_technician():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(
        workflow,
        technician="Sanny",
    )

    summary.set_closure(closure)

    assert summary.closure_technician == "Sanny"


def test_summary_exposes_closure_reason():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(
        workflow,
        reason="Issue resolved after verification.",
    )

    summary.set_closure(closure)

    assert summary.closure_reason == (
        "Issue resolved after verification."
    )


def test_summary_exposes_closure_workflow_state():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure_state is workflow.state
    assert summary.closure_state.value == "RESOLVED"


def test_summary_does_not_create_closure():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert summary.closure is None


def test_summary_does_not_create_closure_metadata():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert summary.closure_id is None
    assert summary.closure_technician is None
    assert summary.closure_reason is None
    assert summary.closure_state is None


def test_setting_closure_does_not_change_workflow():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    state_before = workflow.state
    history_before = list(workflow.history)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state is state_before
    assert workflow.history == history_before


def test_setting_closure_does_not_change_case_evidence():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    findings_before = summary.findings
    root_causes_before = summary.root_causes
    recommendations_before = summary.recommendations

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.findings == findings_before
    assert summary.root_causes == root_causes_before
    assert summary.recommendations == recommendations_before


def test_closure_does_not_become_finding():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.findings == []


def test_closure_does_not_become_root_cause():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.root_causes == []


def test_closure_does_not_become_recommendation():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.recommendations == []


def test_closure_does_not_create_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.reasoning_summary is None

    summary.set_closure(build_closure(workflow))

    assert summary.reasoning_summary is None


def test_closure_does_not_replace_reasoning_summary():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    summary.set_closure(build_closure(workflow))

    assert summary.reasoning_summary is reasoning_summary


def test_closure_does_not_create_decision():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.decision is None

    summary.set_closure(build_closure(workflow))

    assert summary.decision is None


def test_closure_does_not_replace_decision():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    decision = build_decision(workflow)

    summary.set_decision(decision)
    summary.set_closure(build_closure(workflow))

    assert summary.decision is decision


def test_decision_and_closure_remain_separate():
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


def test_closure_identity_survives_summary_access():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    first = summary.closure
    second = summary.closure

    assert first is closure
    assert second is closure
    assert first is second


def test_closure_metadata_remains_stable():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    closure = build_closure(
        workflow,
        technician="Sanny",
        reason="Resolved and verified.",
    )

    summary.set_closure(closure)

    closure_id = summary.closure_id
    technician = summary.closure_technician
    reason = summary.closure_reason
    state = summary.closure_state

    assert summary.closure_id == closure_id
    assert summary.closure_technician == technician
    assert summary.closure_reason == reason
    assert summary.closure_state is state


def test_replacing_closure_updates_only_closure_projection():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    first = build_closure(
        workflow,
        technician="Sanny",
        reason="First closure.",
    )

    second = build_closure(
        workflow,
        technician="Technician 2",
        reason="Updated closure.",
    )

    summary.set_closure(first)

    original_workflow = summary.workflow
    original_decision = summary.decision
    original_findings = summary.findings
    original_root_causes = summary.root_causes
    original_recommendations = summary.recommendations

    summary.set_closure(second)

    assert summary.closure is second
    assert summary.workflow is original_workflow
    assert summary.decision is original_decision
    assert summary.findings == original_findings
    assert summary.root_causes == original_root_causes
    assert summary.recommendations == original_recommendations


def test_closure_belongs_to_summary_workflow():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure.workflow is summary.workflow


def test_summary_rejects_closure_from_different_workflow():
    workflow = build_workflow()
    other_workflow = build_workflow()

    resolve_workflow(workflow)
    resolve_workflow(other_workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(other_workflow)

    try:
        summary.set_closure(closure)
        assert False, "Expected ValueError."
    except ValueError as exc:
        assert str(exc) == "Closure belongs to a different workflow."

    assert summary.closure is None


def test_summary_rejects_invalid_closure():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    try:
        summary.set_closure(object())
        assert False, "Expected ValueError."
    except ValueError as exc:
        assert str(exc) == (
            "Case summary requires a TechnicianCaseClosure."
        )

    assert summary.closure is None


def test_closure_survives_workflow_reopening():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    closure_id = closure.closure_id

    workflow.reopen()

    assert summary.closure is closure
    assert summary.closure_id == closure_id
    assert summary.closure_technician == "Sanny"
    assert summary.closure_reason == "Issue resolved"


def test_closure_does_not_change_after_workflow_reopening():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    original_closure_state = summary.closure_state

    workflow.reopen()

    assert summary.closure_state is original_closure_state
    assert summary.closure_state.value == "RESOLVED"


def test_summary_can_hold_closure_and_reasoning_independently():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    reasoning_summary = build_reasoning_summary(workflow)
    closure = build_closure(workflow)

    summary.set_reasoning_summary(reasoning_summary)
    summary.set_closure(closure)

    assert summary.reasoning_summary is reasoning_summary
    assert summary.closure is closure
    assert summary.reasoning_summary is not summary.closure


def test_summary_can_hold_closure_and_decision_independently():
    workflow = build_workflow()
    resolve_workflow(workflow)

    summary = TechnicianCaseSummary(workflow)

    decision = build_decision(workflow)
    closure = build_closure(workflow)

    summary.set_decision(decision)
    summary.set_closure(closure)

    assert summary.decision is decision
    assert summary.closure is closure
    assert summary.decision is not summary.closure