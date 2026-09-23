class NetworkDiagnosticCase:

    def __init__(
        self,
        observations,
        signals,
        findings,
        correlations,
        candidates,
        evaluations,
        primary_cause,
        confidences,
        explanations,
        recommendations,
    ):
        self.observations = list(observations)
        self.signals = list(signals)
        self.findings = list(findings)
        self.correlations = list(correlations)
        self.candidates = list(candidates)
        self.evaluations = list(evaluations)
        self.primary_cause = primary_cause
        self.confidences = list(confidences)
        self.explanations = list(explanations)
        self.recommendations = list(recommendations)


class NetworkDiagnosticCaseSynthesizer:

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def synthesize(self, evidence):

        results = self.pipeline.diagnose(evidence)

        return self._build_case(results)

    def synthesize_adaptive(self):

        results = self.pipeline.get_adaptive_result()

        return self._build_case(results)

    @staticmethod
    def _build_case(results):

        recommendation = results["recommendation"]

        if recommendation is None:
            recommendations = []
        elif isinstance(recommendation, list):
            recommendations = recommendation
        else:
            recommendations = [recommendation]

        return NetworkDiagnosticCase(
            observations=results["observations"],
            signals=results["signals"],
            findings=results["findings"],
            correlations=results["correlations"],
            candidates=results["candidates"],
            evaluations=results["evaluations"],
            primary_cause=results["primary_cause"],
            confidences=results["confidences"],
            explanations=results["explanations"],
            recommendations=recommendations,
        )
