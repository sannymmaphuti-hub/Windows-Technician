from engine.confidence import Confidence
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_reasoning import RootCauseReasoning
from engine.root_cause_selection import RootCauseSelection
from engine.confidence_rule import ConfidenceRule


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
                assessment="SUPPORTED",
                explanation="Process evidence supports this candidate.",
            ),
            RootCauseEvaluation(
                candidate=candidates[1],
                supporting_evidence=[],
                assessment="INSUFFICIENT",
                explanation="Evidence is insufficient for this candidate.",
            ),
        ]


class FakeConfidenceRule(ConfidenceRule):

    def matches(self, subject, evidence):
        return any(
            evaluation.candidate is subject
            for evaluation in evidence
        )

    def create_confidence(self, subject, evidence):
        evaluation = next(
            evaluation
            for evaluation in evidence
            if evaluation.candidate is subject
        )

        levels = {
            "INSUFFICIENT": "LOW",
            "SUPPORTED": "MEDIUM",
            "STRONGLY_SUPPORTED": "HIGH",
        }

        return Confidence(
            subject=subject.cause_type,
            level=levels[evaluation.assessment],
            explanation="Confidence derived from root-cause evaluation.",
        )


class FakeSelection:

    def select(self, evaluations):
        return evaluations[0].candidate


def create_reasoning():
    confidence_engine = ConfidenceEngine()
    confidence_engine.register_rule(FakeConfidenceRule())

    return RootCauseReasoning(
        candidate_engine=FakeCandidateEngine(),
        evaluation_pipeline=FakeEvaluationPipeline(),
        selection=FakeSelection(),
        confidence_engine=confidence_engine,
    )


def test_root_cause_reasoning_produces_confidence_results():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert "confidences" in result
    assert len(result["confidences"]) == 2


def test_confidence_is_returned_as_confidence_objects():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert all(
        isinstance(confidence, Confidence)
        for confidence in result["confidences"]
    )


def test_supported_candidate_receives_medium_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    confidence = result["confidences"][0]

    assert confidence.subject == "MEMORY_INTENSIVE_PROCESS"
    assert confidence.level == "MEDIUM"


def test_insufficient_candidate_receives_low_confidence():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    confidence = result["confidences"][1]

    assert confidence.subject == "MEMORY_LEAK"
    assert confidence.level == "LOW"


def test_confidence_results_match_candidate_count():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert len(result["candidates"]) == 2
    assert len(result["evaluations"]) == 2
    assert len(result["confidences"]) == 2


def test_confidence_does_not_replace_evaluations():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert result["evaluations"][0].assessment == "SUPPORTED"
    assert result["evaluations"][1].assessment == "INSUFFICIENT"


def test_primary_root_cause_selection_remains_separate():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert result["primary_cause"].cause_type == (
        "MEMORY_INTENSIVE_PROCESS"
    )


def test_confidence_does_not_select_primary_root_cause():
    reasoning = create_reasoning()

    result = reasoning.analyze([])

    assert result["primary_cause"].cause_type == (
        "MEMORY_INTENSIVE_PROCESS"
    )

    assert result["confidences"][1].level == "LOW"