from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_pipeline import RootCauseEvaluationPipeline
from engine.root_cause_selection import RootCauseSelection


class RootCauseReasoning:

    def __init__(
        self,
        candidate_engine=None,
        evaluation_pipeline=None,
        selection=None,
        confidence_engine=None,
    ):
        if candidate_engine is None:
            candidate_engine = RootCauseEngine()

        if evaluation_pipeline is None:
            evaluation_pipeline = RootCauseEvaluationPipeline()

        if selection is None:
            selection = RootCauseSelection()

        if confidence_engine is None:
            confidence_engine = ConfidenceEngine()

        self.candidate_engine = candidate_engine
        self.evaluation_pipeline = evaluation_pipeline
        self.selection = selection
        self.confidence_engine = confidence_engine

    def analyze(self, findings):
        candidates = self.candidate_engine.detect(findings)

        evaluations = self.evaluation_pipeline.evaluate(
            candidates,
            findings,
        )

        confidences = []

        for candidate in candidates:
            candidate_confidences = self.confidence_engine.evaluate(
                candidate,
                evaluations,
            )

            confidences.extend(candidate_confidences)

        primary_cause = self.selection.select(evaluations)

        return {
            "findings": findings,
            "candidates": candidates,
            "evaluations": evaluations,
            "confidences": confidences,
            "primary_cause": primary_cause,
        }
