import pytest

from engine.finding import Finding
from engine.fleet import Fleet
from engine.fleet_problem import FleetProblem
from engine.fleet_problem_pattern import FleetProblemPattern
from engine.fleet_recommendation_context import FleetRecommendationContext
from engine.fleet_recommendation_intelligence import FleetRecommendationIntelligence
from engine.fleet_root_cause_evidence import FleetRootCauseEvidence
from engine.fleet_root_cause_reasoning import FleetRootCauseReasoning
from engine.managed_machine import ManagedMachine
from engine.recommendation import Recommendation
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


def make_machine(machine_id):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=machine_id,
    )


def make_fleet():
    fleet = Fleet("Safety Fleet")
    fleet.add_machine(make_machine("m1"))
    fleet.add_machine(make_machine("m2"))
    fleet.add_machine(make_machine("m3"))
    return fleet


def make_pattern(machine_ids=None, fleet_machine_count=3):
    return FleetProblemPattern(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        machine_ids=machine_ids or ["m1", "m2"],
        fleet_machine_count=fleet_machine_count,
    )


def make_finding():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="MEDIUM",
        description="Fleet CPU pressure detected.",
    )


def make_candidate():
    return RootCauseCandidate(
        cause_type="CPU_RESOURCE_DEMAND",
        category="CPU",
        explanation="Possible high CPU resource demand.",
    )


def make_context(
    primary_cause=True,
    assessment="SUPPORTED",
    evaluations=True,
):
    finding = make_finding()
    candidate = make_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[finding],
        assessment=assessment,
        explanation="CPU evidence evaluated.",
    )

    return FleetRecommendationContext(
        pattern=make_pattern(),
        finding=finding,
        candidates=[candidate],
        evaluations=[evaluation] if evaluations else [],
        confidences=[],
        primary_cause=candidate if primary_cause else None,
    )


# ---------------------------------------------------------------------------
# Fleet problem validation
# ---------------------------------------------------------------------------

def test_fleet_problem_rejects_invalid_problem_type():
    with pytest.raises(ValueError):
        FleetProblem(
            problem_type="",
            domain="CPU",
            severity="HIGH",
            machine_ids=["m1"],
        )


def test_fleet_problem_rejects_invalid_domain():
    with pytest.raises(ValueError):
        FleetProblem(
            problem_type="CPU_PRESSURE",
            domain="",
            severity="HIGH",
            machine_ids=["m1"],
        )


def test_fleet_problem_rejects_invalid_severity():
    with pytest.raises(ValueError):
        FleetProblem(
            problem_type="CPU_PRESSURE",
            domain="CPU",
            severity="UNKNOWN",
            machine_ids=["m1"],
        )


# ---------------------------------------------------------------------------
# Pattern safety
# ---------------------------------------------------------------------------

def test_pattern_type_is_derived_and_not_mutable_input():
    pattern = FleetProblemPattern(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        machine_ids=["m1"],
        fleet_machine_count=3,
    )

    assert pattern.pattern_type == "ISOLATED"
    assert not hasattr(pattern, "_pattern_type")


def test_pattern_rejects_negative_fleet_machine_count():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type="CPU_PRESSURE",
            domain="CPU",
            machine_ids=["m1"],
            fleet_machine_count=-1,
        )


def test_pattern_rejects_machine_count_smaller_than_affected_count():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type="CPU_PRESSURE",
            domain="CPU",
            machine_ids=["m1", "m2"],
            fleet_machine_count=1,
        )


# ---------------------------------------------------------------------------
# Fleet isolation
# ---------------------------------------------------------------------------

def test_root_cause_evidence_preserves_machine_identity():
    pattern = make_pattern(["m1", "m3"])

    evidence = FleetRootCauseEvidence(pattern)
    finding = evidence.to_finding()

    assert finding.supporting_signals[0]["machine_ids"] == ["m1", "m3"]


def test_fleet_reasoning_rejects_invalid_pattern():
    reasoning = FleetRootCauseReasoning(
        root_cause_reasoning=object(),
    )

    with pytest.raises(ValueError):
        reasoning.analyze(object())


def test_fleet_reasoning_does_not_infer_causality_from_machine_count():
    context = make_context(
        primary_cause=False,
        evaluations=False,
    )

    intelligence = FleetRecommendationIntelligence()

    assert intelligence.generate(context) == []


# ---------------------------------------------------------------------------
# Root-cause safety
# ---------------------------------------------------------------------------

def test_context_rejects_invalid_pattern():
    with pytest.raises(ValueError):
        FleetRecommendationContext(
            pattern=object(),
            finding=make_finding(),
            candidates=[],
            evaluations=[],
            confidences=[],
            primary_cause=None,
        )


def test_context_rejects_non_list_candidates():
    with pytest.raises(ValueError):
        FleetRecommendationContext(
            pattern=make_pattern(),
            finding=make_finding(),
            candidates=None,
            evaluations=[],
            confidences=[],
            primary_cause=None,
        )


def test_context_rejects_non_list_evaluations():
    with pytest.raises(ValueError):
        FleetRecommendationContext(
            pattern=make_pattern(),
            finding=make_finding(),
            candidates=[],
            evaluations=None,
            confidences=[],
            primary_cause=None,
        )


def test_context_rejects_non_list_confidences():
    with pytest.raises(ValueError):
        FleetRecommendationContext(
            pattern=make_pattern(),
            finding=make_finding(),
            candidates=[],
            evaluations=[],
            confidences=None,
            primary_cause=None,
        )


# ---------------------------------------------------------------------------
# Recommendation safety
# ---------------------------------------------------------------------------

def test_recommendation_intelligence_rejects_invalid_context():
    intelligence = FleetRecommendationIntelligence()

    with pytest.raises(ValueError):
        intelligence.generate(object())


def test_insufficient_evidence_generates_no_recommendation():
    context = make_context(
        assessment="INSUFFICIENT",
    )

    intelligence = FleetRecommendationIntelligence()

    assert intelligence.generate(context) == []


def test_missing_primary_cause_generates_no_recommendation():
    context = make_context(
        primary_cause=False,
    )

    intelligence = FleetRecommendationIntelligence()

    assert intelligence.generate(context) == []


def test_missing_evaluations_generates_no_recommendation():
    context = make_context(
        evaluations=False,
    )

    intelligence = FleetRecommendationIntelligence()

    assert intelligence.generate(context) == []


def test_valid_recommendation_is_canonical_recommendation():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(context)

    assert len(recommendations) == 1
    assert isinstance(recommendations[0], Recommendation)


# ---------------------------------------------------------------------------
# Authorization / remediation boundary
# ---------------------------------------------------------------------------

def test_recommendation_has_no_authorization_state():
    context = make_context()

    recommendation = FleetRecommendationIntelligence().generate(context)[0]

    assert not hasattr(recommendation, "authorization")
    assert not hasattr(recommendation, "authorized")


def test_recommendation_has_no_execution_state():
    context = make_context()

    recommendation = FleetRecommendationIntelligence().generate(context)[0]

    assert not hasattr(recommendation, "executed")
    assert not hasattr(recommendation, "execution")


def test_recommendation_has_no_remediation_result():
    context = make_context()

    recommendation = FleetRecommendationIntelligence().generate(context)[0]

    assert not hasattr(recommendation, "remediation_result")
    assert not hasattr(recommendation, "result")


def test_fleet_recommendation_does_not_execute_remediation():
    context = make_context()

    recommendations = FleetRecommendationIntelligence().generate(context)

    assert recommendations
    assert all(
        not hasattr(recommendation, "execute")
        for recommendation in recommendations
    )