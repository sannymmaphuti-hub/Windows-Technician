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
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    case = type(
        "Case",
        (),
        {
            "case_id": "case-decision-001",
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
        description="Investigate the detected issue.",
        rationale="The evidence requires technician review.",
    )


def build_decision(workflow):
    recommendation = build_recommendation()

    return TechnicianDecision(
        workflow=workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Technician accepted the recommendation.",
    )


def build_summary():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)
    return workflow, summary


def test_case_summary_has_no_decision_before_one_is_set():
    _, summary = build_summary()

    assert summary.decision is None


def test_case_summary_preserves_decision_identity():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision is decision


def test_case_summary_preserves_decision_type():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.ACCEPT
    )


def test_case_summary_preserves_recommendation_identity():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision.recommendation is decision.recommendation


def test_case_summary_preserves_workflow_identity_through_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision.workflow is workflow
    assert summary.decision.workflow is summary.workflow


def test_case_summary_preserves_decision_notes():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.decision.notes == (
        "Technician accepted the recommendation."
    )


def test_setting_a_new_decision_replaces_the_previous_decision():
    workflow, summary = build_summary()

    first_decision = build_decision(workflow)

    second_decision = TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=TechnicianDecisionType.DEFER,
        notes="Decision deferred for additional evidence.",
    )

    summary.set_decision(first_decision)
    assert summary.decision is first_decision

    summary.set_decision(second_decision)

    assert summary.decision is second_decision
    assert summary.decision is not first_decision
    assert summary.decision.decision_type is (
        TechnicianDecisionType.DEFER
    )


def test_setting_decision_does_not_change_case_evidence():
    workflow, summary = build_summary()

    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_decision_remains_available_through_workflow_lifecycle():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert summary.decision is decision
    assert summary.decision.workflow is workflow


def test_decision_remains_available_after_resolution():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.is_terminal
    assert summary.decision is decision
    assert summary.decision.workflow is workflow


def test_decision_remains_available_after_reopen():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    workflow.reopen()

    assert summary.workflow_state.value == "INVESTIGATING"
    assert summary.decision is decision
    assert summary.decision.workflow is workflow


def test_decision_does_not_create_a_reasoning_summary():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.reasoning_summary is None


def test_decision_and_reasoning_summary_remain_separate():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )

    summary.set_decision(decision)
    summary.set_reasoning_summary(reasoning_summary)

    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning_summary
    assert summary.decision is not summary.reasoning_summary


def test_decision_does_not_change_reasoning_overview_counts():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )

    summary.set_reasoning_summary(reasoning_summary)

    before = reasoning_summary.overview

    summary.set_decision(decision)

    after = reasoning_summary.overview

    assert before["finding_count"] == after["finding_count"]
    assert before["correlation_count"] == after["correlation_count"]
    assert before["root_cause_count"] == after["root_cause_count"]
    assert before["recommendation_count"] == (
        after["recommendation_count"]
    )