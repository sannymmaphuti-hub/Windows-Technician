from engine.confidence import Confidence
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_evaluation import RootCauseEvaluation


def create_candidate(cause_type):
    return RootCauseCandidate(
        cause_type=cause_type,
        category="MEMORY",
        explanation=f"{cause_type} may be contributing.",
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


def test_engine_can_generate_confidence_for_multiple_candidates():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "INSUFFICIENT",
    )

    engine = create_engine()

    confidences_a = engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )

    confidences_b = engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )

    assert len(confidences_a) == 1
    assert len(confidences_b) == 1


def test_multiple_candidates_receive_independent_confidence_levels():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "INSUFFICIENT",
    )

    engine = create_engine()

    confidence_a = engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )[0]

    confidence_b = engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )[0]

    assert confidence_a.level == "MEDIUM"
    assert confidence_b.level == "LOW"


def test_stronger_candidate_can_have_higher_confidence_than_competing_candidate():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "STRONGLY_SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "SUPPORTED",
    )

    engine = create_engine()

    confidence_a = engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )[0]

    confidence_b = engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )[0]

    assert confidence_a.level == "HIGH"
    assert confidence_b.level == "MEDIUM"


def test_confidence_is_not_selected_as_primary_root_cause():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "SUPPORTED",
    )

    engine = create_engine()

    confidence_a = engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )[0]

    confidence_b = engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )[0]

    assert confidence_a.level == "MEDIUM"
    assert confidence_b.level == "MEDIUM"

    assert not hasattr(confidence_a, "primary")
    assert not hasattr(confidence_b, "primary")


def test_confidence_results_belong_to_their_respective_candidates():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    confidence_a = engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )[0]

    confidence_b = engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )[0]

    assert isinstance(confidence_a, Confidence)
    assert isinstance(confidence_b, Confidence)

    assert confidence_a.subject == "MEMORY_INTENSIVE_PROCESS"
    assert confidence_b.subject == "MEMORY_LEAK"


def test_confidence_does_not_change_when_unrelated_evaluation_is_added():
    candidate = create_candidate("MEMORY_INTENSIVE_PROCESS")
    unrelated_candidate = create_candidate("MEMORY_LEAK")

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )
    unrelated_evaluation = create_evaluation(
        unrelated_candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    confidence_without_unrelated = engine.evaluate(
        candidate,
        [evaluation],
    )[0]

    confidence_with_unrelated = engine.evaluate(
        candidate,
        [
            evaluation,
            unrelated_evaluation,
        ],
    )[0]

    assert (
        confidence_without_unrelated.level
        == confidence_with_unrelated.level
    )


def test_confidence_does_not_mutate_multiple_evaluations():
    candidate_a = create_candidate("MEMORY_INTENSIVE_PROCESS")
    candidate_b = create_candidate("MEMORY_LEAK")

    evaluation_a = create_evaluation(
        candidate_a,
        "SUPPORTED",
    )
    evaluation_b = create_evaluation(
        candidate_b,
        "INSUFFICIENT",
    )

    original_a = evaluation_a.assessment
    original_b = evaluation_b.assessment

    engine = create_engine()

    engine.evaluate(
        candidate_a,
        [evaluation_a, evaluation_b],
    )

    engine.evaluate(
        candidate_b,
        [evaluation_a, evaluation_b],
    )

    assert evaluation_a.assessment == original_a
    assert evaluation_b.assessment == original_b