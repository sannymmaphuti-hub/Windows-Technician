from engine.confidence import Confidence
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_evaluation import RootCauseEvaluation


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation="A memory-intensive process may be contributing.",
    )


def create_evaluation(candidate, assessment):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Evaluation result.",
    )


def create_engine():
    engine = ConfidenceEngine()
    engine.register_rule(RootCauseConfidenceRule())
    return engine


def test_confidence_engine_can_evaluate_root_cause_confidence():
    candidate = create_candidate()
    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1


def test_supported_root_cause_produces_medium_confidence():
    candidate = create_candidate()
    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert confidences[0].level == "MEDIUM"


def test_strongly_supported_root_cause_produces_high_confidence():
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert confidences[0].level == "HIGH"


def test_insufficient_root_cause_produces_low_confidence():
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert confidences[0].level == "LOW"


def test_confidence_is_returned_as_confidence_object():
    candidate = create_candidate()
    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert isinstance(confidences[0], Confidence)


def test_confidence_belongs_to_correct_root_cause():
    candidate = create_candidate()
    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert confidences[0].subject == "MEMORY_INTENSIVE_PROCESS"


def test_unrelated_candidate_produces_no_confidence():
    candidate = create_candidate()

    unrelated_candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A memory leak may be contributing.",
    )

    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    engine = create_engine()

    confidences = engine.evaluate(
        unrelated_candidate,
        [evaluation],
    )

    assert confidences == []


def test_confidence_pipeline_does_not_modify_evaluation():
    candidate = create_candidate()
    evaluation = create_evaluation(
    candidate,
    "SUPPORTED",
    )

    original_assessment = evaluation.assessment
    original_candidate = evaluation.candidate

    engine = create_engine()

    engine.evaluate(
        candidate,
        [evaluation],
    )

    assert evaluation.assessment == original_assessment
    assert evaluation.candidate is original_candidate