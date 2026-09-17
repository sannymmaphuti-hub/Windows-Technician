from engine.confidence import Confidence
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_pipeline import RootCauseEvaluationPipeline
from engine.root_cause_reasoning import RootCauseReasoning
from engine.root_cause_selection import RootCauseSelection


class FakeCandidateEngine:

    def detect(self, findings):
        return [
            RootCauseCandidate(
                cause_type="MEMORY_INTENSIVE_PROCESS",
                category="MEMORY",
                explanation="A memory-intensive process may be contributing.",
            ),
            RootCauseCandidate(
                cause_type="MEMORY_LEAK",
                category="MEMORY",
                explanation="A memory leak may be contributing.",
            ),
        ]


class FakeEvaluationPipeline:

    def evaluate(self, candidates, findings):
        return [
            RootCauseEvaluation(
                candidate=candidates[0],
                supporting_evidence=[],
                assessment="STRONGLY_SUPPORTED",
                explanation="Process evidence strongly supports this candidate.",
            ),
            RootCauseEvaluation(
                candidate=candidates[1],
                supporting_evidence=[],
                assessment="INSUFFICIENT",
                explanation="Evidence is insufficient for this candidate.",
            ),
        ]


def create_reasoning():
    confidence_engine = ConfidenceEngine()
    confidence_engine.register_rule(
        RootCauseConfidenceRule()
    )

    return RootCauseReasoning(
        candidate_engine=FakeCandidateEngine(),
        evaluation_pipeline=FakeEvaluationPipeline(),
        selection=RootCauseSelection(),
        confidence_engine=confidence_engine,
    )


def test_real_confidence_rule_produces_confidence_results():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert len(result["confidences"]) == 2


def test_strongly_supported_candidate_receives_high_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    confidence = result["confidences"][0]

    assert confidence.level == "HIGH"


def test_insufficient_candidate_receives_low_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    confidence = result["confidences"][1]

    assert confidence.level == "LOW"


def test_real_confidence_results_are_confidence_objects():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert all(
        isinstance(confidence, Confidence)
        for confidence in result["confidences"]
    )


def test_multiple_candidates_receive_independent_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert len(result["confidences"]) == 2
    assert result["confidences"][0].level == "HIGH"
    assert result["confidences"][1].level == "LOW"


def test_confidence_does_not_replace_evaluations():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert len(result["evaluations"]) == 2
    assert result["evaluations"][0].assessment == "STRONGLY_SUPPORTED"
    assert result["evaluations"][1].assessment == "INSUFFICIENT"


def test_primary_selection_remains_independent_of_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert result["primary_cause"] is result["candidates"][0]


def test_confidence_rule_does_not_select_primary_cause():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert result["primary_cause"].cause_type == (
        "MEMORY_INTENSIVE_PROCESS"
    )