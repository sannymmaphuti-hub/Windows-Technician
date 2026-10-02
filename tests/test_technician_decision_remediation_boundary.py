from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow

from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action_planner import (
    RemediationActionPlanner,
)
from engine.remediation_action import RemediationAction
from engine.remediation_decision_boundary import (
    RemediationDecisionBoundary,
)
from engine.remediation_eligibility import RemediationEligibility


def build_workflow():
    case = type(
        "Case",
        (),
        {
            "case_id": "decision-remediation-001",
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()

    return TechnicianWorkflow(case)


def build_recommendation(
    priority="HIGH",
    recommendation_type="TEST_RECOMMENDATION",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category="MEMORY",
        priority=priority,
        description="Review high memory usage.",
        rationale="Memory pressure requires technician review.",
    )


def build_decision(
    workflow,
    recommendation,
    decision_type=TechnicianDecisionType.ACCEPT,
):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=recommendation,
        decision_type=decision_type,
        notes="Technician decision recorded.",
    )


def build_action(recommendation):
    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(
        recommendation
    )

    return planner.create_action(planner_input)


def test_accept_decision_does_not_authorize_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert action.authorization_status == "UNAUTHORIZED"


def test_accept_decision_does_not_execute_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert action.execution_status == "NOT_EXECUTED"


def test_reject_decision_does_not_authorize_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.REJECT,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.REJECT
    )
    assert action.authorization_status == "UNAUTHORIZED"


def test_defer_decision_does_not_authorize_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.DEFER,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.DEFER
    )
    assert action.authorization_status == "UNAUTHORIZED"


def test_investigate_further_does_not_authorize_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.INVESTIGATE_FURTHER
    )
    assert action.authorization_status == "UNAUTHORIZED"


def test_escalate_decision_does_not_authorize_remediation_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.decision_type is (
        TechnicianDecisionType.ESCALATE
    )
    assert action.authorization_status == "UNAUTHORIZED"


def test_decision_preserves_the_exact_recommendation_used_for_remediation():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.recommendation is recommendation


def test_remediation_boundary_evaluates_recommendation_independently():
    recommendation = build_recommendation(
        priority="HIGH"
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.recommendation_type == (
        recommendation.recommendation_type
    )
    assert decision.eligible is True


def test_medium_recommendation_is_not_remediation_eligible():
    recommendation = build_recommendation(
        priority="MEDIUM"
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False


def test_low_recommendation_is_not_remediation_eligible():
    recommendation = build_recommendation(
        priority="LOW"
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False


def test_critical_recommendation_is_remediation_eligible():
    recommendation = build_recommendation(
        priority="CRITICAL"
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True


def test_planner_creates_unauthorized_action_from_eligible_recommendation():
    recommendation = build_recommendation(
        priority="HIGH"
    )

    action = build_action(recommendation)

    assert isinstance(action, RemediationAction)
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_medium_recommendation_can_create_action_but_is_not_boundary_eligible():
    recommendation = build_recommendation(
        priority="MEDIUM"
    )

    boundary = RemediationDecisionBoundary()
    decision = boundary.evaluate(recommendation)

    action = build_action(recommendation)

    assert action is not None
    assert action.severity == "WARNING"
    assert decision.eligible is False

def test_planner_does_not_create_action_for_low_recommendation():
    recommendation = build_recommendation(
        priority="LOW"
    )

    action = build_action(recommendation)

    assert action is None


def test_planner_creates_action_for_critical_recommendation():
    recommendation = build_recommendation(
        priority="CRITICAL"
    )

    action = build_action(recommendation)

    assert isinstance(action, RemediationAction)
    assert action.severity == "CRITICAL"
    assert action.authorization_status == "UNAUTHORIZED"


def test_unauthorized_action_is_not_eligible_for_execution():
    recommendation = build_recommendation(
        priority="HIGH"
    )

    action = build_action(recommendation)

    action.operation = lambda: None

    eligibility = RemediationEligibility()

    assert eligibility.is_eligible(action) is False
    assert eligibility.get_reason(action) == "NOT_AUTHORIZED"


def test_accept_decision_alone_does_not_make_action_eligible():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    action = build_action(recommendation)
    action.operation = lambda: None

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    eligibility = RemediationEligibility()

    assert summary.decision is decision
    assert action.authorization_status == "UNAUTHORIZED"
    assert eligibility.is_eligible(action) is False
    assert eligibility.get_reason(action) == "NOT_AUTHORIZED"


def test_explicit_authorization_is_separate_from_accept_decision():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    action = build_action(recommendation)
    action.operation = lambda: None

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_explicit_authorization_then_makes_action_eligible():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    action = build_action(recommendation)
    action.operation = lambda: None

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    action.authorize()

    eligibility = RemediationEligibility()

    assert summary.decision is decision
    assert eligibility.is_eligible(action) is True
    assert eligibility.get_reason(action) == "ELIGIBLE"


def test_decision_does_not_execute_authorized_action():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    executed = []

    action = build_action(recommendation)
    action.operation = lambda: executed.append(True)
    action.authorize()

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []


def test_decision_remains_separate_from_remediation_action_identity():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.decision is not action
    assert summary.decision.recommendation is recommendation


def test_decision_and_remediation_action_share_recommendation_but_not_state():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
    )

    action = build_action(recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.recommendation is recommendation

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert summary.decision.decision_type is (
        TechnicianDecisionType.ACCEPT
    )


def test_reject_decision_does_not_destroy_or_mutate_recommendation():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.REJECT,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.recommendation is recommendation
    assert recommendation.priority == "HIGH"
    assert recommendation.category == "MEMORY"


def test_escalate_decision_does_not_destroy_or_mutate_recommendation():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation,
        TechnicianDecisionType.ESCALATE,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(decision)

    assert summary.decision.recommendation is recommendation
    assert recommendation.priority == "HIGH"
    assert recommendation.category == "MEMORY"