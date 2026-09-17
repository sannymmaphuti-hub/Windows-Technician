from engine.network_diagnostic_case_synthesis import NetworkDiagnosticCase


def create_case(
    observations=None,
    signals=None,
    findings=None,
    correlations=None,
    candidates=None,
    evaluations=None,
    primary_cause=None,
    confidences=None,
    explanations=None,
    recommendations=None,
):
    return NetworkDiagnosticCase(
        observations=[] if observations is None else observations,
        signals=[] if signals is None else signals,
        findings=[] if findings is None else findings,
        correlations=[] if correlations is None else correlations,
        candidates=[] if candidates is None else candidates,
        evaluations=[] if evaluations is None else evaluations,
        primary_cause=primary_cause,
        confidences=[] if confidences is None else confidences,
        explanations=[] if explanations is None else explanations,
        recommendations=[] if recommendations is None else recommendations,
    )


def test_case_exposes_all_diagnostic_layers():
    case = create_case()

    assert hasattr(case, "observations")
    assert hasattr(case, "signals")
    assert hasattr(case, "findings")
    assert hasattr(case, "correlations")
    assert hasattr(case, "candidates")
    assert hasattr(case, "evaluations")
    assert hasattr(case, "primary_cause")
    assert hasattr(case, "confidences")
    assert hasattr(case, "explanations")
    assert hasattr(case, "recommendations")


def test_case_collection_layers_are_lists():
    case = create_case()

    assert isinstance(case.observations, list)
    assert isinstance(case.signals, list)
    assert isinstance(case.findings, list)
    assert isinstance(case.correlations, list)
    assert isinstance(case.candidates, list)
    assert isinstance(case.evaluations, list)
    assert isinstance(case.confidences, list)
    assert isinstance(case.explanations, list)
    assert isinstance(case.recommendations, list)


def test_case_primary_cause_can_be_none():
    case = create_case(primary_cause=None)

    assert case.primary_cause is None


def test_case_preserves_primary_cause_object():
    primary_cause = object()

    case = create_case(primary_cause=primary_cause)

    assert case.primary_cause is primary_cause


def test_case_preserves_layer_order():
    observations = ["observation-1", "observation-2"]
    signals = ["signal-1", "signal-2"]
    findings = ["finding-1", "finding-2"]
    correlations = ["correlation-1", "correlation-2"]
    candidates = ["candidate-1", "candidate-2"]
    evaluations = ["evaluation-1", "evaluation-2"]
    confidences = ["confidence-1", "confidence-2"]
    explanations = ["explanation-1", "explanation-2"]
    recommendations = ["recommendation-1", "recommendation-2"]

    case = create_case(
        observations=observations,
        signals=signals,
        findings=findings,
        correlations=correlations,
        candidates=candidates,
        evaluations=evaluations,
        confidences=confidences,
        explanations=explanations,
        recommendations=recommendations,
    )

    assert case.observations == observations
    assert case.signals == signals
    assert case.findings == findings
    assert case.correlations == correlations
    assert case.candidates == candidates
    assert case.evaluations == evaluations
    assert case.confidences == confidences
    assert case.explanations == explanations
    assert case.recommendations == recommendations


def test_case_copies_collection_inputs():
    observations = ["observation"]
    signals = ["signal"]
    findings = ["finding"]
    correlations = ["correlation"]
    candidates = ["candidate"]
    evaluations = ["evaluation"]
    confidences = ["confidence"]
    explanations = ["explanation"]
    recommendations = ["recommendation"]

    case = create_case(
        observations=observations,
        signals=signals,
        findings=findings,
        correlations=correlations,
        candidates=candidates,
        evaluations=evaluations,
        confidences=confidences,
        explanations=explanations,
        recommendations=recommendations,
    )

    assert case.observations is not observations
    assert case.signals is not signals
    assert case.findings is not findings
    assert case.correlations is not correlations
    assert case.candidates is not candidates
    assert case.evaluations is not evaluations
    assert case.confidences is not confidences
    assert case.explanations is not explanations
    assert case.recommendations is not recommendations


def test_mutating_original_collection_does_not_change_case():
    observations = ["observation"]
    recommendations = ["recommendation"]

    case = create_case(
        observations=observations,
        recommendations=recommendations,
    )

    observations.append("new-observation")
    recommendations.append("new-recommendation")

    assert case.observations == ["observation"]
    assert case.recommendations == ["recommendation"]


def test_mutating_case_collection_does_not_change_original_input():
    observations = ["observation"]
    recommendations = ["recommendation"]

    case = create_case(
        observations=observations,
        recommendations=recommendations,
    )

    case.observations.append("case-observation")
    case.recommendations.append("case-recommendation")

    assert observations == ["observation"]
    assert recommendations == ["recommendation"]


def test_empty_case_is_valid():
    case = create_case()

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

from engine.observation import Observation
from engine.signal import Signal
from engine.finding import Finding
from engine.correlation import Correlation
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.recommendation import Recommendation


def test_case_accepts_real_v05_layer_objects():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=True,
    )

    signal = Signal(
        signal_type="NETWORK_ADAPTER_DISCONNECTED",
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    finding = Finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        category="NETWORK",
        severity="HIGH",
        description="The network adapter is disconnected.",
        supporting_signals=[signal],
    )

    correlation = Correlation(
        correlation_type="NETWORK_ADAPTER_FAILURE",
        findings=[finding],
        strength="HIGH",
        explanation="A disconnected network adapter may be related to the loss of network connectivity.",
    )

    candidate = RootCauseCandidate(
        cause_type="NETWORK_ADAPTER_FAILURE",
        category="NETWORK",
        explanation="The network adapter may be contributing to the connectivity problem.",
    )

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[finding],
        assessment="STRONGLY_SUPPORTED",
        explanation="The evidence strongly supports the network adapter as a possible cause.",
    )

    confidence = Confidence(
        subject="NETWORK_ADAPTER_FAILURE",
        level="HIGH",
        explanation="The available evidence provides high confidence.",
    )

    explanation = Explanation(
        subject="NETWORK_ADAPTER_FAILURE",
        summary="The network adapter may be causing the connection problem.",
        details="The available network evidence indicates that the adapter may be contributing to the connectivity issue.",
        confidence="HIGH",
    )

    recommendation = Recommendation(
        recommendation_type="REVIEW_NETWORK_ADAPTER",
        category="NETWORK",
        priority="HIGH",
        description="Review the network adapter and its connection.",
        rationale="The available evidence identifies the adapter as a possible contributor.",
    )

    case = create_case(
        observations=[observation],
        signals=[signal],
        findings=[finding],
        correlations=[correlation],
        candidates=[candidate],
        evaluations=[evaluation],
        primary_cause=candidate,
        confidences=[confidence],
        explanations=[explanation],
        recommendations=[recommendation],
    )

    assert all(isinstance(item, Observation) for item in case.observations)
    assert all(isinstance(item, Signal) for item in case.signals)
    assert all(isinstance(item, Finding) for item in case.findings)
    assert all(isinstance(item, Correlation) for item in case.correlations)
    assert all(isinstance(item, RootCauseCandidate) for item in case.candidates)
    assert all(isinstance(item, RootCauseEvaluation) for item in case.evaluations)
    assert isinstance(case.primary_cause, RootCauseCandidate)
    assert all(isinstance(item, Confidence) for item in case.confidences)
    assert all(isinstance(item, Explanation) for item in case.explanations)
    assert all(isinstance(item, Recommendation) for item in case.recommendations)


def test_case_preserves_real_v05_objects_by_identity():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=True,
    )

    signal = Signal(
        signal_type="NETWORK_ADAPTER_DISCONNECTED",
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    finding = Finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        category="NETWORK",
        severity="HIGH",
        description="The network adapter is disconnected.",
        supporting_signals=[signal],
    )

    case = create_case(
        observations=[observation],
        signals=[signal],
        findings=[finding],
    )

    assert case.observations[0] is observation
    assert case.signals[0] is signal
    assert case.findings[0] is finding

def test_case_preserves_nested_layer_relationships():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    signal = Signal(
        signal_type="NETWORK_ADAPTER_DISCONNECTED",
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    finding = Finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        category="NETWORK",
        severity="HIGH",
        description="The network adapter is disconnected.",
        supporting_signals=[signal],
    )

    correlation = Correlation(
        correlation_type="NETWORK_ADAPTER_FAILURE",
        findings=[finding],
        strength="HIGH",
        explanation="The disconnected adapter may be related to the connectivity problem.",
    )

    case = create_case(
        observations=[observation],
        signals=[signal],
        findings=[finding],
        correlations=[correlation],
    )

    assert case.findings[0].supporting_signals[0] is signal
    assert case.correlations[0].findings[0] is finding

def test_case_preserves_complete_layer_identity():
    observation_1 = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=True,
    )
    observation_2 = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=True,
    )

    signal_1 = Signal(
        signal_type="NETWORK_ADAPTER_DISCONNECTED",
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )
    signal_2 = Signal(
        signal_type="DNS_RESOLUTION_FAILED",
        source="network",
        subject="network_dns",
        attribute="working",
        value=False,
    )

    finding_1 = Finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        category="NETWORK",
        severity="HIGH",
        description="The network adapter is disconnected.",
        supporting_signals=[signal_1],
    )
    finding_2 = Finding(
        finding_type="DNS_RESOLUTION_FAILURE",
        category="NETWORK",
        severity="MEDIUM",
        description="DNS resolution is failing.",
        supporting_signals=[signal_2],
    )

    correlation = Correlation(
        correlation_type="NETWORK_ADAPTER_FAILURE",
        findings=[finding_1],
        strength="HIGH",
        explanation="The disconnected adapter may be related to the connectivity problem.",
    )

    candidate = RootCauseCandidate(
        cause_type="NETWORK_ADAPTER_FAILURE",
        category="NETWORK",
        explanation="The network adapter may be contributing to the connectivity problem.",
    )

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[finding_1],
        assessment="STRONGLY_SUPPORTED",
        explanation="The evidence strongly supports the candidate.",
    )

    confidence = Confidence(
        subject="NETWORK_ADAPTER_FAILURE",
        level="HIGH",
        explanation="The available evidence provides high confidence.",
    )

    explanation = Explanation(
        subject="NETWORK_ADAPTER_FAILURE",
        summary="The network adapter may be causing the connection problem.",
        details="The available network evidence indicates that the adapter may be contributing to the connectivity issue.",
        confidence="HIGH",
    )

    recommendation = Recommendation(
        recommendation_type="REVIEW_NETWORK_ADAPTER",
        category="NETWORK",
        priority="HIGH",
        description="Review the network adapter and its connection.",
        rationale="The available evidence identifies the adapter as a possible contributor.",
    )

    case = create_case(
        observations=[observation_1, observation_2],
        signals=[signal_1, signal_2],
        findings=[finding_1, finding_2],
        correlations=[correlation],
        candidates=[candidate],
        evaluations=[evaluation],
        primary_cause=candidate,
        confidences=[confidence],
        explanations=[explanation],
        recommendations=[recommendation],
    )

    assert case.observations == [observation_1, observation_2]
    assert case.signals == [signal_1, signal_2]
    assert case.findings == [finding_1, finding_2]
    assert case.correlations == [correlation]
    assert case.candidates == [candidate]
    assert case.evaluations == [evaluation]
    assert case.primary_cause is candidate
    assert case.confidences == [confidence]
    assert case.explanations == [explanation]
    assert case.recommendations == [recommendation]