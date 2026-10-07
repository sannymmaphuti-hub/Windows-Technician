from engine.cpu_resource_demand_root_cause_rule import (
    CpuResourceDemandRootCauseRule,
)
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.fleet_problem_pattern import FleetProblemPattern
from engine.fleet_root_cause_evidence import FleetRootCauseEvidence
from engine.fleet_root_cause_reasoning import FleetRootCauseReasoning
from engine.root_cause_reasoning import RootCauseReasoning


def make_pattern():
    return FleetProblemPattern(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        machine_ids=["m1", "m2", "m3"],
        fleet_machine_count=10,
    )


def make_reasoning():
    candidate_engine = RootCauseEngine()
    candidate_engine.register_rule(
        CpuResourceDemandRootCauseRule()
    )

    evaluation_engine = RootCauseEvaluationEngine()

    from engine.cpu_resource_demand_evaluation_rule import (
        CpuResourceDemandEvaluationRule,
    )

    evaluation_engine.register_rule(
        CpuResourceDemandEvaluationRule()
    )

    evaluation_pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    confidence_engine = ConfidenceEngine()
    confidence_engine.register_rule(
        RootCauseConfidenceRule()
    )

    return RootCauseReasoning(
        candidate_engine=candidate_engine,
        evaluation_pipeline=evaluation_pipeline,
        confidence_engine=confidence_engine,
    )


def test_evidence_adapter_requires_pattern():
    try:
        FleetRootCauseEvidence(None)
    except ValueError:
        return

    assert False


def test_evidence_adapter_creates_existing_finding():
    pattern = make_pattern()

    finding = FleetRootCauseEvidence(pattern).to_finding()

    assert finding.finding_type == "CPU_PRESSURE"
    assert finding.category == "CPU"
    assert finding.severity == "MEDIUM"


def test_fleet_finding_preserves_distribution():
    pattern = make_pattern()

    finding = FleetRootCauseEvidence(pattern).to_finding()

    evidence = finding.supporting_signals[0]

    assert evidence["fleet_scope"] == "REPEATED"
    assert evidence["affected_machine_count"] == 3
    assert evidence["fleet_machine_count"] == 10
    assert evidence["affected_machine_ratio"] == 0.3
    assert evidence["machine_ids"] == ["m1", "m2", "m3"]


def test_fleet_finding_does_not_change_pattern():
    pattern = make_pattern()
    original_ids = list(pattern.machine_ids)

    FleetRootCauseEvidence(pattern).to_finding()

    assert pattern.machine_ids == original_ids


def test_fleet_reasoning_requires_root_cause_reasoning():
    try:
        FleetRootCauseReasoning(None)
    except ValueError:
        return

    assert False


def test_fleet_reasoning_requires_pattern():
    reasoning = FleetRootCauseReasoning(make_reasoning())

    try:
        reasoning.analyze(None)
    except ValueError:
        return

    assert False


def test_fleet_reasoning_reuses_existing_root_cause_candidate():
    reasoning = FleetRootCauseReasoning(make_reasoning())

    result = reasoning.analyze(make_pattern())

    assert len(result["candidates"]) == 1
    assert result["candidates"][0].cause_type == (
        "CPU_RESOURCE_DEMAND"
    )


def test_fleet_reasoning_returns_pattern_and_finding():
    reasoning = FleetRootCauseReasoning(make_reasoning())
    pattern = make_pattern()

    result = reasoning.analyze(pattern)

    assert result["pattern"] is pattern
    assert result["finding"].finding_type == "CPU_PRESSURE"


def test_fleet_reasoning_does_not_create_new_candidate_type():
    reasoning = FleetRootCauseReasoning(make_reasoning())

    result = reasoning.analyze(make_pattern())

    assert all(
        candidate.__class__.__name__ == "RootCauseCandidate"
        for candidate in result["candidates"]
    )


def test_fleet_reasoning_does_not_authorize_remediation():
    reasoning = FleetRootCauseReasoning(make_reasoning())

    result = reasoning.analyze(make_pattern())

    assert not hasattr(result, "authorization")
    assert not hasattr(result, "remediation")
    assert "authorization" not in result
    assert "remediation" not in result
    assert "recovery" not in result
