from engine.finding import Finding
from engine.fleet_problem_pattern import FleetProblemPattern
from engine.fleet_recommendation_context import (
    FleetRecommendationContext,
)
from engine.fleet_recommendation_intelligence import (
    FleetRecommendationIntelligence,
)
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.recommendation import Recommendation


def make_pattern(
    machine_ids=None,
    fleet_machine_count=10,
):
    return FleetProblemPattern(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        machine_ids=machine_ids or ["m1", "m2", "m3"],
        fleet_machine_count=fleet_machine_count,
    )


def make_context(
    pattern=None,
    assessment="SUPPORTED",
    primary_cause=True,
    evaluations=True,
):
    pattern = pattern or make_pattern()

    finding = Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="MEDIUM",
        description="Fleet CPU pressure detected.",
    )

    candidate = RootCauseCandidate(
        cause_type="CPU_RESOURCE_DEMAND",
        category="CPU",
        explanation=(
            "Evidence supports unusually high CPU resource demand."
        ),
    )

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[finding],
        assessment=assessment,
        explanation=(
            "Evidence supports CPU resource demand."
        ),
    )

    return FleetRecommendationContext(
        pattern=pattern,
        finding=finding,
        candidates=[candidate],
        evaluations=[evaluation] if evaluations else [],
        confidences=[],
        primary_cause=candidate if primary_cause else None,
    )


def test_context_requires_pattern():
    try:
        FleetRecommendationContext(
            pattern=None,
            finding=object(),
            candidates=[],
            evaluations=[],
            confidences=[],
            primary_cause=None,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for missing pattern.")


def test_context_requires_lists():
    pattern = make_pattern()

    try:
        FleetRecommendationContext(
            pattern=pattern,
            finding=object(),
            candidates=None,
            evaluations=[],
            confidences=[],
            primary_cause=None,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid candidates.")


def test_context_preserves_fleet_distribution():
    context = make_context()

    assert context.affected_machine_count == 3
    assert context.fleet_machine_count == 10
    assert context.affected_machine_ratio == 0.3
    assert context.pattern_type == "REPEATED"


def test_context_evidence_contains_distribution():
    context = make_context()

    evidence = context.to_evidence()

    assert evidence["affected_machine_count"] == 3
    assert evidence["fleet_machine_count"] == 10
    assert evidence["affected_machine_ratio"] == 0.3
    assert evidence["pattern_type"] == "REPEATED"
    assert evidence["machine_ids"] == ["m1", "m2", "m3"]


def test_context_preserves_root_cause():
    context = make_context()

    assert context.primary_cause is context.candidates[0]
    assert context.primary_cause.cause_type == "CPU_RESOURCE_DEMAND"


def test_supported_root_cause_generates_recommendation():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == "fleet_investigation"


def test_repeated_pattern_has_medium_priority():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert recommendations[0].priority == "MEDIUM"


def test_widespread_pattern_has_high_priority():
    context = make_context(
        make_pattern(
            machine_ids=["m1", "m2", "m3", "m4", "m5"],
            fleet_machine_count=10,
        )
    )

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert len(recommendations) == 1
    assert recommendations[0].priority == "HIGH"


def test_recommendation_preserves_domain():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert recommendations[0].category == "CPU"


def test_insufficient_root_cause_produces_no_recommendation():
    context = make_context(assessment="INSUFFICIENT")

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert recommendations == []


def test_missing_primary_cause_produces_no_recommendation():
    context = make_context(primary_cause=False)

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert recommendations == []


def test_missing_evaluations_produces_no_recommendation():
    context = make_context(evaluations=False)

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert recommendations == []


def test_result_uses_existing_recommendation_model():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert isinstance(recommendations[0], Recommendation)


def test_recommendation_contains_no_authorization():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    evidence = recommendations[0].to_evidence()

    assert "authorization" not in evidence
    assert "authorized" not in evidence


def test_recommendation_contains_no_execution():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    evidence = recommendations[0].to_evidence()

    assert "execution" not in evidence
    assert "executed" not in evidence


def test_recommendation_contains_no_remediation_result():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    evidence = recommendations[0].to_evidence()

    assert "remediation_result" not in evidence
    assert "remediation" not in evidence


def test_machine_distribution_is_not_lost():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(
        context
    )

    assert context.pattern.machine_ids == ["m1", "m2", "m3"]
    assert context.affected_machine_count == 3
    assert context.affected_machine_ratio == 0.3
