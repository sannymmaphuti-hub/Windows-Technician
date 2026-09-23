from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation_intelligence import RecommendationIntelligence
from engine.recommendation_remediation_adapter import RecommendationRemediationAdapter
from engine.remediation_action_planner import RemediationActionPlanner
from engine.remediation_decision_boundary import RemediationDecisionBoundary
from engine.remediation_verifier import RemediationVerifier


def _high_memory_finding():
    return Finding(
        finding_type="MEMORY",
        description="High memory usage detected.",
        category="MEMORY",
        severity="HIGH",
        supporting_signals=[],
    )


def test_full_intelligence_to_verification_flow():
    case = DiagnosticCase()
    case.findings = [_high_memory_finding()]

    recommendations = case.generate_recommendations()

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    boundary = RemediationDecisionBoundary()
    decision = boundary.evaluate(recommendation)

    assert decision.recommendation_type == "memory_review"
    assert decision.eligible is True

    adapter = RecommendationRemediationAdapter()
    planner_input = adapter.to_planner_input(recommendation)

    assert planner_input["category"] == "MEMORY"
    assert planner_input["severity"] == "WARNING"

    planner = RemediationActionPlanner()
    action = planner.create_action(planner_input)

    assert action is not None
    assert action.authorization_status != "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    verifier = RemediationVerifier()

    verification = verifier.verify(
        expected={"memory_pressure": "NORMAL"},
        observed={"memory_pressure": "NORMAL"},
        action_id=action.action_id,
    )

    assert verification["verified"] is True
    assert verification["action_id"] == action.action_id


def test_full_flow_blocks_medium_recommendation_before_remediation():
    case = DiagnosticCase()

    case.findings = [
        Finding(
            finding_type="MEMORY",
            description="Moderate memory usage detected.",
            category="MEMORY",
            severity="MEDIUM",
            supporting_signals=[],
        )
    ]

    recommendations = case.generate_recommendations()

    assert recommendations == []


def test_full_flow_handles_unsupported_finding_without_remediation():
    case = DiagnosticCase()

    case.findings = [
        Finding(
            finding_type="UNKNOWN",
            description="Unsupported condition.",
            category="UNKNOWN",
            severity="CRITICAL",
            supporting_signals=[],
        )
    ]

    recommendations = case.generate_recommendations()

    assert recommendations == []


def test_full_flow_preserves_remediation_safety_boundary():
    case = DiagnosticCase()
    case.findings = [_high_memory_finding()]

    recommendations = case.generate_recommendations()
    recommendation = recommendations[0]

    decision = RemediationDecisionBoundary().evaluate(recommendation)

    assert decision.eligible is True

    planner_input = RecommendationRemediationAdapter().to_planner_input(
        recommendation
    )

    action = RemediationActionPlanner().create_action(planner_input)

    assert action.authorization_status != "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_full_flow_verification_detects_unsuccessful_remediation():
    case = DiagnosticCase()
    case.findings = [_high_memory_finding()]

    recommendation = case.generate_recommendations()[0]

    decision = RemediationDecisionBoundary().evaluate(recommendation)

    assert decision.eligible is True

    planner_input = RecommendationRemediationAdapter().to_planner_input(
        recommendation
    )

    action = RemediationActionPlanner().create_action(planner_input)

    verifier = RemediationVerifier()

    verification = verifier.verify(
        expected={"memory_pressure": "NORMAL"},
        observed={"memory_pressure": "HIGH"},
        action_id=action.action_id,
    )

    assert verification["verified"] is False
    assert verification["action_id"] == action.action_id