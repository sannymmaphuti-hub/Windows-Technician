from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_selection import RootCauseSelection

from tests.test_network_root_cause_pipeline import (
    create_root_cause_engine,
    create_evaluation_engine,
    create_finding_engine,
    create_correlation_engine,
    disconnected_adapter_evidence,
    local_network_failure_evidence,
    dns_failure_evidence,
    internet_failure_evidence,
    healthy_network_evidence,
)


def create_confidence_engine():

    engine = ConfidenceEngine()

    engine.register_rule(
        RootCauseConfidenceRule()
    )

    return engine


def diagnose_network_confidence(evidence):

    observation_builder = __import__(
        "engine.network_observation_builder",
        fromlist=["NetworkObservationBuilder"],
    ).NetworkObservationBuilder()

    signal_detector = __import__(
        "engine.observation_to_signal",
        fromlist=["ObservationToSignal"],
    ).ObservationToSignal()

    finding_engine = create_finding_engine()
    correlation_engine = create_correlation_engine()
    root_cause_engine = create_root_cause_engine()
    evaluation_engine = create_evaluation_engine()
    selection = RootCauseSelection()
    confidence_engine = create_confidence_engine()

    observations = observation_builder.build(evidence)

    signals = []
    findings = []

    for observation in observations:

        signal = signal_detector.detect(
            observation
        )

        if signal is None:
            continue

        signals.append(signal)
        findings.extend(
            finding_engine.detect(signal)
        )

    correlations = correlation_engine.detect(
        findings
    )

    candidates = root_cause_engine.detect(
        findings
    )

    evaluations = []

    for candidate in candidates:

        evaluations.extend(
            evaluation_engine.evaluate(
                candidate,
                findings,
            )
        )

    primary = selection.select(
        evaluations
    )

    confidences = []

    if primary is not None:

        confidences = confidence_engine.evaluate(
            primary,
            evaluations,
        )

    return (
        observations,
        signals,
        findings,
        correlations,
        candidates,
        evaluations,
        primary,
        confidences,
    )


def test_dns_failure_reaches_medium_confidence():

    result = diagnose_network_confidence(
        dns_failure_evidence()
    )

    primary = result[6]
    confidences = result[7]

    assert primary is not None
    assert primary.cause_type == "DNS_FAILURE"

    assert len(confidences) == 1
    assert confidences[0].level == "MEDIUM"


def test_local_network_failure_reaches_high_confidence():

    result = diagnose_network_confidence(
        local_network_failure_evidence()
    )

    primary = result[6]
    confidences = result[7]

    assert primary is not None
    assert primary.cause_type == "LOCAL_NETWORK_FAILURE"

    assert len(confidences) == 1
    assert confidences[0].level == "HIGH"


def test_disconnected_adapter_reaches_high_confidence():

    result = diagnose_network_confidence(
        disconnected_adapter_evidence()
    )

    primary = result[6]
    confidences = result[7]

    assert primary is not None
    assert primary.cause_type == "NETWORK_ADAPTER_FAILURE"

    assert len(confidences) == 1
    assert confidences[0].level == "HIGH"


def test_internet_failure_alone_has_no_root_cause_confidence():

    result = diagnose_network_confidence(
        internet_failure_evidence()
    )

    primary = result[6]
    confidences = result[7]

    assert primary is None
    assert confidences == []


def test_healthy_network_has_no_root_cause_confidence():

    result = diagnose_network_confidence(
        healthy_network_evidence()
    )

    primary = result[6]
    confidences = result[7]

    assert primary is None
    assert confidences == []