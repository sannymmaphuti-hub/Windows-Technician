from engine.diagnostic_engine import DiagnosticEngine
from engine.root_cause_reasoning import RootCauseReasoning
from engine.rules.memory_rule import MemoryUsageRule


def create_engine(explanation_engine=None):
    engine = DiagnosticEngine(
        root_cause_reasoning=RootCauseReasoning(),
        explanation_engine=explanation_engine,
    )

    engine.add_rule(MemoryUsageRule())

    return engine

def create_memory_evidence():
    return {
        "MEMORY": {
            "usage_percent": 95,
        }
    }


def test_diagnostic_engine_can_accept_explanation_engine():
    from engine.explanation_engine import ExplanationEngine

    explanation_engine = ExplanationEngine()

    engine = create_engine(
            explanation_engine=explanation_engine
        )

    assert engine.explanation_engine is explanation_engine


def test_diagnostic_engine_preserves_existing_findings():
    engine = create_engine()

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "findings" in result
    assert result["total_findings"] == len(
        result["findings"]
    )


def test_diagnostic_engine_preserves_root_cause_reasoning():
    engine = create_engine()

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "root_cause_reasoning" in result

    reasoning = result["root_cause_reasoning"]

    assert "candidates" in reasoning
    assert "evaluations" in reasoning
    assert "confidences" in reasoning
    assert "primary_cause" in reasoning


def test_diagnostic_engine_can_return_explanations():
    from engine.explanation_engine import ExplanationEngine
    from engine.finding_explanation_rule import (
        FindingExplanationRule,
    )

    explanation_engine = ExplanationEngine()
    explanation_engine.register_rule(
        FindingExplanationRule()
    )

    engine = create_engine(
        explanation_engine=explanation_engine
    )

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "explanations" in result
    assert isinstance(result["explanations"], list)


def test_diagnostic_engine_explanations_contain_explanation_objects():
    from engine.explanation import Explanation
    from engine.explanation_engine import ExplanationEngine
    from engine.finding_explanation_rule import (
        FindingExplanationRule,
    )

    explanation_engine = ExplanationEngine()
    explanation_engine.register_rule(
        FindingExplanationRule()
    )

    engine = create_engine(
        explanation_engine=explanation_engine
    )

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert result["explanations"]

    for explanation in result["explanations"]:
        assert isinstance(explanation, Explanation)


def test_diagnostic_engine_explanations_do_not_replace_findings():
    from engine.explanation_engine import ExplanationEngine
    from engine.finding_explanation_rule import (
        FindingExplanationRule,
    )

    explanation_engine = ExplanationEngine()
    explanation_engine.register_rule(
        FindingExplanationRule()
    )

    engine = create_engine(
        explanation_engine=explanation_engine
    )

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert result["findings"]
    assert result["explanations"]

    assert result["findings"] != result["explanations"]


def test_diagnostic_engine_works_without_explanation_engine():
    engine = DiagnosticEngine(
        root_cause_reasoning=RootCauseReasoning()
    )

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "findings" in result
    assert "recommendations" in result
    assert "explanations" not in result


def test_diagnostic_engine_preserves_recommendations():
    engine = create_engine()

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "recommendations" in result


def test_diagnostic_engine_preserves_status():
    engine = create_engine()

    result = engine.diagnose(
        create_memory_evidence()
    )

    assert "status" in result


def test_diagnostic_engine_explanation_integration_does_not_mutate_findings():
    from engine.explanation_engine import ExplanationEngine
    from engine.finding_explanation_rule import (
        FindingExplanationRule,
    )

    explanation_engine = ExplanationEngine()
    explanation_engine.register_rule(
        FindingExplanationRule()
    )

    engine = create_engine(
        explanation_engine=explanation_engine
    )

    result = engine.diagnose(
        create_memory_evidence()
    )

    findings_before = list(result["findings"])

    result_again = engine.diagnose(
        create_memory_evidence()
    )

    assert result["findings"] == findings_before
    assert result_again["findings"]