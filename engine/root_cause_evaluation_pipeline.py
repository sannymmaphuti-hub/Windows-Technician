from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)


class RootCauseEvaluationPipeline:

    def __init__(
        self,
        evaluation_engine=None,
    ):

        if evaluation_engine is None:
            evaluation_engine = RootCauseEvaluationEngine()

        self.evaluation_engine = evaluation_engine

    def evaluate(
        self,
        candidates,
        findings,
    ):

        evaluations = []

        for candidate in candidates:

            candidate_evaluations = (
                self.evaluation_engine.evaluate(
                    candidate,
                    findings,
                )
            )

            evaluations.extend(
                candidate_evaluations
            )

        return evaluations
