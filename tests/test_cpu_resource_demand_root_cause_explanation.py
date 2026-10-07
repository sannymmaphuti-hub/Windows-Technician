from engine.confidence_engine import ConfidenceEngine
from engine.cpu_resource_demand_evaluation_rule import (
    CpuResourceDemandEvaluationRule,
)
from engine.cpu_resource_demand_root_cause_rule import (
    CpuResourceDemandRootCauseRule,
)
from engine.explanation import Explanation
from engine.explanation_engine import ExplanationEngine
from engine.finding import Finding
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_evaluation_pipeline import RootCauseEvaluationPipeline
from engine.root_cause_explanation_rule import RootCauseExplanationRule
from engine.root_cause_reasoning import RootCauseReasoning


def create_cpu_pressure():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="CPU pressure detected.",
        supporting_signals=[],
    )


def build_reasoning():
    candidate_engine = RootCauseEngine()
    candidate_engine.register_rule(
        CpuResourceDemandRootCauseRule()
    )

    evaluation_engine = RootCauseEvaluationEngine()
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


def build_explanation_engine():
    explanation_engine = ExplanationEngine()
    explanation_engine.register_rule(
        RootCauseExplanationRule()
    )
    return explanation_engine


def test_cpu_resource_demand_produces_root_cause_explanation():
    reasoning = build_reasoning()
    result = reasoning.analyze([
        create_cpu_pressure(),
    ])

    candidate = result["candidates"][0]
    evaluations = result["evaluations"]

    explanation_engine = build_explanation_engine()

    explanations = explanation_engine.evaluate(
        candidate,
        evaluations,
    )

    assert len(explanations) == 1
    assert isinstance(explanations[0], Explanation)


def test_cpu_resource_demand_explanation_preserves_subject():
    reasoning_result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    candidate = reasoning_result["candidates"][0]

    explanations = build_explanation_engine().evaluate(
        candidate,
        reasoning_result["evaluations"],
    )

    explanation = explanations[0]

    assert explanation.subject == "CPU_RESOURCE_DEMAND"


def test_cpu_resource_demand_explanation_describes_insufficient_evidence():
    reasoning_result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    candidate = reasoning_result["candidates"][0]

    explanation = build_explanation_engine().evaluate(
        candidate,
        reasoning_result["evaluations"],
    )[0]

    assert (
        "not enough evidence"
        in explanation.summary.lower()
    )

    assert (
        "further investigation"
        in explanation.details.lower()
    )


def test_cpu_resource_demand_explanation_does_not_claim_certainty():
    reasoning_result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    candidate = reasoning_result["candidates"][0]

    explanation = build_explanation_engine().evaluate(
        candidate,
        reasoning_result["evaluations"],
    )[0]

    assert "certain" not in explanation.summary.lower()
    assert "confirmed" not in explanation.summary.lower()


def test_cpu_resource_demand_explanation_matches_evaluation():
    reasoning_result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    candidate = reasoning_result["candidates"][0]
    evaluation = reasoning_result["evaluations"][0]

    explanation = build_explanation_engine().evaluate(
        candidate,
        [evaluation],
    )[0]

    assert evaluation.assessment == "INSUFFICIENT"
    assert explanation.subject == candidate.cause_type
    assert explanation.summary
    assert explanation.details