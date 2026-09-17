import pytest

from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
)


def create_case_inputs():

    observations = [
        "observation-1",
        "observation-2",
    ]

    signals = [
        "signal-1",
    ]

    findings = [
        "finding-1",
    ]

    correlations = [
        "correlation-1",
    ]

    candidates = [
        "candidate-1",
    ]

    evaluations = [
        "evaluation-1",
    ]

    primary_cause = "primary-cause"

    confidences = [
        "confidence-1",
    ]

    explanations = [
        "explanation-1",
    ]

    recommendations = [
        "recommendation-1",
    ]

    return {
        "observations": observations,
        "signals": signals,
        "findings": findings,
        "correlations": correlations,
        "candidates": candidates,
        "evaluations": evaluations,
        "primary_cause": primary_cause,
        "confidences": confidences,
        "explanations": explanations,
        "recommendations": recommendations,
    }


def test_network_diagnostic_case_can_be_created():

    case = NetworkDiagnosticCase(
        **create_case_inputs()
    )

    assert case is not None


def test_network_diagnostic_case_preserves_observations():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.observations == inputs["observations"]


def test_network_diagnostic_case_preserves_signals():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.signals == inputs["signals"]


def test_network_diagnostic_case_preserves_findings():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.findings == inputs["findings"]


def test_network_diagnostic_case_preserves_correlations():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.correlations == inputs["correlations"]


def test_network_diagnostic_case_preserves_root_cause_information():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.candidates == inputs["candidates"]
    assert case.evaluations == inputs["evaluations"]
    assert case.primary_cause == inputs["primary_cause"]


def test_network_diagnostic_case_preserves_confidence():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.confidences == inputs["confidences"]


def test_network_diagnostic_case_preserves_explanations():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.explanations == inputs["explanations"]


def test_network_diagnostic_case_preserves_recommendations():

    inputs = create_case_inputs()

    case = NetworkDiagnosticCase(**inputs)

    assert case.recommendations == inputs["recommendations"]


def test_network_diagnostic_case_supports_no_primary_cause():

    inputs = create_case_inputs()
    inputs["primary_cause"] = None

    case = NetworkDiagnosticCase(**inputs)

    assert case.primary_cause is None


def test_network_diagnostic_case_supports_empty_diagnostic_results():

    case = NetworkDiagnosticCase(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        evaluations=[],
        primary_cause=None,
        confidences=[],
        explanations=[],
        recommendations=[],
    )

    assert case.observations == []
    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.candidates == []
    assert case.evaluations == []
    assert case.primary_cause is None
    assert case.confidences == []
    assert case.explanations == []
    assert case.recommendations == []


def test_network_diagnostic_case_does_not_mutate_inputs():

    inputs = create_case_inputs()

    original = {
        key: value.copy() if isinstance(value, list) else value
        for key, value in inputs.items()
    }

    NetworkDiagnosticCase(**inputs)

    assert inputs == original


def test_network_diagnostic_case_rejects_missing_required_arguments():

    inputs = create_case_inputs()

    del inputs["recommendations"]

    with pytest.raises(TypeError):
        NetworkDiagnosticCase(**inputs)

def test_network_diagnostic_case_synthesizer_exists():

    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCaseSynthesizer,
    )

    assert NetworkDiagnosticCaseSynthesizer is not None

class StubPipeline:

    def diagnose(self, evidence):
        return {
            "observations": ["observation"],
            "signals": ["signal"],
            "findings": ["finding"],
            "correlations": ["correlation"],
            "candidates": ["candidate"],
            "evaluations": ["evaluation"],
            "primary_cause": "primary-cause",
            "confidences": ["confidence"],
            "explanations": ["explanation"],
            "recommendation": ["recommendation"],
        }


def create_synthesizer():

    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCaseSynthesizer,
    )

    return NetworkDiagnosticCaseSynthesizer(
        pipeline=StubPipeline()
    )


def test_synthesizer_can_be_created():

    synthesizer = create_synthesizer()

    assert synthesizer is not None


def test_synthesizer_produces_network_diagnostic_case():

    synthesizer = create_synthesizer()

    case = synthesizer.synthesize(
        {"network": "evidence"}
    )

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )


def test_synthesizer_preserves_pipeline_results():

    synthesizer = create_synthesizer()

    case = synthesizer.synthesize(
        {"network": "evidence"}
    )

    assert case.observations == ["observation"]
    assert case.signals == ["signal"]
    assert case.findings == ["finding"]
    assert case.correlations == ["correlation"]
    assert case.candidates == ["candidate"]
    assert case.evaluations == ["evaluation"]
    assert case.primary_cause == "primary-cause"
    assert case.confidences == ["confidence"]
    assert case.explanations == ["explanation"]
    assert case.recommendations == ["recommendation"]


def test_synthesizer_passes_evidence_to_pipeline():

    class RecordingPipeline:

        def __init__(self):
            self.received_evidence = None

        def diagnose(self, evidence):
            self.received_evidence = evidence

            return {
                "observations": [],
                "signals": [],
                "findings": [],
                "correlations": [],
                "candidates": [],
                "evaluations": [],
                "primary_cause": None,
                "confidences": [],
                "explanations": [],
                "recommendation": [],
            }

    pipeline = RecordingPipeline()

    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCaseSynthesizer,
    )

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline=pipeline
    )

    evidence = {
        "network": "evidence"
    }

    synthesizer.synthesize(evidence)

    assert pipeline.received_evidence == evidence


def test_synthesizer_supports_no_primary_cause():

    class NoCausePipeline:

        def diagnose(self, evidence):
            return {
                "observations": [],
                "signals": ["signal"],
                "findings": [],
                "correlations": [],
                "candidates": [],
                "evaluations": [],
                "primary_cause": None,
                "confidences": [],
                "explanations": [],
                "recommendation": [],
            }

    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCaseSynthesizer,
    )

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline=NoCausePipeline()
    )

    case = synthesizer.synthesize({})

    assert case.primary_cause is None
    assert case.signals == ["signal"]


def test_synthesizer_does_not_mutate_pipeline_results():

    class MutablePipeline:

        def __init__(self):
            self.results = {
                "observations": ["observation"],
                "signals": ["signal"],
                "findings": ["finding"],
                "correlations": ["correlation"],
                "candidates": ["candidate"],
                "evaluations": ["evaluation"],
                "primary_cause": "primary-cause",
                "confidences": ["confidence"],
                "explanations": ["explanation"],
                "recommendation": ["recommendation"],
            }

        def diagnose(self, evidence):
            return self.results

    pipeline = MutablePipeline()

    original = {
        key: value.copy() if isinstance(value, list) else value
        for key, value in pipeline.results.items()
    }

    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCaseSynthesizer,
    )

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline=pipeline
    )

    synthesizer.synthesize({})

    assert pipeline.results == original

def test_network_case_synthesizer_can_synthesize_from_adaptive_pipeline():
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )
    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCase,
        NetworkDiagnosticCaseSynthesizer,
    )

    translator = DiagnosticOutcomeToObservation()
    pipeline = NetworkDiagnosticPipeline()

    gateway_outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    internet_outcome = DiagnosticActionOutcome(
        action_type="TEST_INTERNET_CONNECTIVITY",
        evidence={
            "internet_reachable": False,
        },
    )

    gateway_observation = translator.translate(
        gateway_outcome
    )

    internet_observation = translator.translate(
        internet_outcome
    )

    pipeline.process_observation(
        gateway_observation
    )

    pipeline.process_observation(
        internet_observation
    )

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    case = synthesizer.synthesize_adaptive()

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )

    assert case.observations
    assert case.signals
    assert case.findings
    assert case.correlations
    assert case.candidates
    assert case.evaluations
    assert case.primary_cause is not None
    assert case.confidences
    assert case.recommendations

def test_network_pipeline_exposes_adaptive_result_boundary():
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    pipeline = NetworkDiagnosticPipeline()

    assert hasattr(
        pipeline,
        "get_adaptive_result",
    )

    result = pipeline.get_adaptive_result()

    assert isinstance(
        result,
        dict,
    )

    assert "observations" in result
    assert "signals" in result
    assert "findings" in result
    assert "correlations" in result
    assert "candidates" in result
    assert "evaluations" in result
    assert "primary_cause" in result
    assert "confidences" in result
    assert "recommendation" in result

def test_network_case_synthesizer_uses_adaptive_result_boundary():
    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCase,
        NetworkDiagnosticCaseSynthesizer,
    )

    class BoundaryPipeline:

        def get_adaptive_result(self):
            return {
                "observations": ["observation"],
                "signals": ["signal"],
                "findings": ["finding"],
                "correlations": ["correlation"],
                "candidates": ["candidate"],
                "evaluations": ["evaluation"],
                "primary_cause": "primary",
                "confidences": ["confidence"],
                "explanations": [],
                "recommendation": "recommendation",
            }

    pipeline = BoundaryPipeline()

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    case = synthesizer.synthesize_adaptive()

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )

    assert case.observations == ["observation"]
    assert case.signals == ["signal"]
    assert case.findings == ["finding"]
    assert case.correlations == ["correlation"]
    assert case.candidates == ["candidate"]
    assert case.evaluations == ["evaluation"]
    assert case.primary_cause == "primary"
    assert case.confidences == ["confidence"]
    assert case.explanations == []
    assert case.recommendations == ["recommendation"]

def test_network_pipeline_can_reset_adaptive_session():
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    translator = DiagnosticOutcomeToObservation()
    pipeline = NetworkDiagnosticPipeline()

    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    observation = translator.translate(outcome)

    pipeline.process_observation(
        observation
    )

    before_reset = pipeline.get_adaptive_result()

    assert before_reset["observations"]
    assert before_reset["signals"]
    assert before_reset["findings"]

    assert hasattr(
        pipeline,
        "reset_adaptive",
    )

    pipeline.reset_adaptive()

    after_reset = pipeline.get_adaptive_result()

    assert after_reset["observations"] == []
    assert after_reset["signals"] == []
    assert after_reset["findings"] == []
    assert after_reset["correlations"] == []
    assert after_reset["candidates"] == []
    assert after_reset["evaluations"] == []
    assert after_reset["primary_cause"] is None
    assert after_reset["confidences"] == []
    assert after_reset["recommendation"] == []

def test_network_pipeline_adaptive_sessions_are_isolated():
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    translator = DiagnosticOutcomeToObservation()
    pipeline = NetworkDiagnosticPipeline()

    failure_outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    failure_observation = translator.translate(
        failure_outcome
    )

    first_result = pipeline.process_observation(
        failure_observation
    )

    assert first_result["observations"]
    assert first_result["signals"]
    assert first_result["findings"]

    pipeline.reset_adaptive()

    healthy_outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": True,
        },
    )

    healthy_observation = translator.translate(
        healthy_outcome
    )

    second_result = pipeline.process_observation(
        healthy_observation
    )

    assert len(second_result["observations"]) == 1
    assert second_result["observations"][0].value is True

    assert second_result["signals"] == []
    assert second_result["findings"] == []
    assert second_result["correlations"] == []
    assert second_result["candidates"] == []
    assert second_result["evaluations"] == []
    assert second_result["primary_cause"] is None
    assert second_result["confidences"] == []
    assert second_result["recommendation"] == []

def test_network_case_synthesizer_uses_shared_case_construction():
    from engine.network_diagnostic_case_synthesis import (
        NetworkDiagnosticCase,
        NetworkDiagnosticCaseSynthesizer,
    )

    class BoundaryPipeline:

        def diagnose(self, evidence):
            return {
                "observations": ["observation"],
                "signals": ["signal"],
                "findings": ["finding"],
                "correlations": ["correlation"],
                "candidates": ["candidate"],
                "evaluations": ["evaluation"],
                "primary_cause": "primary",
                "confidences": ["confidence"],
                "explanations": ["explanation"],
                "recommendation": "recommendation",
            }

        def get_adaptive_result(self):
            return {
                "observations": ["observation"],
                "signals": ["signal"],
                "findings": ["finding"],
                "correlations": ["correlation"],
                "candidates": ["candidate"],
                "evaluations": ["evaluation"],
                "primary_cause": "primary",
                "confidences": ["confidence"],
                "explanations": ["explanation"],
                "recommendation": "recommendation",
            }

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        BoundaryPipeline()
    )

    normal_case = synthesizer.synthesize({})
    adaptive_case = synthesizer.synthesize_adaptive()

    assert isinstance(
        normal_case,
        NetworkDiagnosticCase,
    )

    assert isinstance(
        adaptive_case,
        NetworkDiagnosticCase,
    )

    assert normal_case.__dict__ == adaptive_case.__dict__