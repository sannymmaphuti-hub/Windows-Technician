from engine.confidence_engine import ConfidenceEngine
from engine.cpu_resource_demand_evaluation_rule import (
    CpuResourceDemandEvaluationRule,
)
from engine.cpu_resource_demand_root_cause_rule import (
    CpuResourceDemandRootCauseRule,
)
from engine.finding import Finding
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.root_cause_evaluation_pipeline import RootCauseEvaluationPipeline
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


def test_cpu_resource_demand_reaches_root_cause_reasoning():
    result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    assert len(result["candidates"]) == 1
    assert result["candidates"][0].cause_type == "CPU_RESOURCE_DEMAND"


def test_cpu_resource_demand_produces_evaluation():
    result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    assert len(result["evaluations"]) == 1

    evaluation = result["evaluations"][0]

    assert evaluation.candidate is result["candidates"][0]
    assert evaluation.assessment == "INSUFFICIENT"


def test_cpu_resource_demand_produces_low_confidence():
    result = build_reasoning().analyze([
        create_cpu_pressure(),
    ])

    assert len(result["confidences"]) == 1
    assert result["confidences"][0].subject == "CPU_RESOURCE_DEMAND"
    assert result["confidences"][0].level == "LOW"


def test_cpu_resource_demand_reasoning_preserves_input_findings():
    findings = [
        create_cpu_pressure(),
    ]

    result = build_reasoning().analyze(findings)

    assert result["findings"] is findings