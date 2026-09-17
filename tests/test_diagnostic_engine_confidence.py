from engine.confidence import Confidence
from engine.confidence_engine import ConfidenceEngine
from engine.diagnostic_engine import DiagnosticEngine
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_reasoning import RootCauseReasoning


def create_confidence_reasoning():
    confidence_engine = ConfidenceEngine()
    confidence_engine.register_rule(
        RootCauseConfidenceRule()
    )

    return RootCauseReasoning(
        confidence_engine=confidence_engine
    )


def create_engine():
    return DiagnosticEngine(
        root_cause_reasoning=create_confidence_reasoning()
    )


def create_evidence():
    return {
        "CPU": {
            "usage_percent": 95
        },
        "MEMORY": {
            "usage_percent": 95
        }
    }


def test_diagnostic_engine_returns_root_cause_reasoning():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    assert "root_cause_reasoning" in result


def test_diagnostic_engine_returns_confidences():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    assert "confidences" in result["root_cause_reasoning"]


def test_diagnostic_engine_confidences_are_confidence_objects():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    confidences = result["root_cause_reasoning"]["confidences"]

    assert all(
        isinstance(confidence, Confidence)
        for confidence in confidences
    )


def test_diagnostic_engine_preserves_evaluations():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    reasoning = result["root_cause_reasoning"]

    assert "evaluations" in reasoning


def test_diagnostic_engine_preserves_primary_root_cause():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    reasoning = result["root_cause_reasoning"]

    assert "primary_cause" in reasoning

def test_diagnostic_engine_confidence_count_matches_evaluation_count():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    reasoning = result["root_cause_reasoning"]

    assert len(reasoning["confidences"]) == len(
        reasoning["evaluations"]
    )


def test_diagnostic_engine_confidence_covers_all_candidates():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    reasoning = result["root_cause_reasoning"]

    assert len(reasoning["confidences"]) == len(
        reasoning["candidates"]
    )


def test_diagnostic_engine_confidence_has_subjects():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    confidences = result["root_cause_reasoning"]["confidences"]

    assert all(
        confidence.subject
        for confidence in confidences
    )


def test_diagnostic_engine_confidence_does_not_expose_probability():
    engine = create_engine()

    result = engine.diagnose(create_evidence())

    confidences = result["root_cause_reasoning"]["confidences"]

    for confidence in confidences:
        evidence = confidence.to_evidence()

        assert "probability" not in evidence
        assert "percentage" not in evidence