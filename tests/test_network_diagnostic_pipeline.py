from engine.finding_engine import FindingEngine
from engine.network_adapter_finding_rule import (
    NetworkAdapterFindingRule,
)
from engine.local_network_unreachable_rule import (
    LocalNetworkUnreachableRule,
)
from engine.dns_resolution_failure_rule import (
    DNSResolutionFailureRule,
)
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.network_observation_builder import (
    NetworkObservationBuilder,
)
from engine.observation_to_signal import ObservationToSignal
from engine.network_diagnostic_pipeline import (
    NetworkDiagnosticPipeline,
)

def create_finding_engine():
    engine = FindingEngine()

    engine.register_rule(NetworkAdapterFindingRule())
    engine.register_rule(LocalNetworkUnreachableRule())
    engine.register_rule(DNSResolutionFailureRule())
    engine.register_rule(InternetConnectivityFailureRule())

    return engine


def diagnose_network_evidence(evidence):
    observation_builder = NetworkObservationBuilder()
    signal_detector = ObservationToSignal()
    finding_engine = create_finding_engine()

    observations = observation_builder.build(evidence)

    signals = []
    findings = []

    for observation in observations:
        signal = signal_detector.detect(observation)

        if signal is None:
            continue

        signals.append(signal)
        findings.extend(finding_engine.detect(signal))

    return observations, signals, findings


def test_network_pipeline_detects_dns_failure():
    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "internet_reachable": False,
        "dns_working": False,
    }

    observations, signals, findings = diagnose_network_evidence(
        evidence
    )

    assert len(observations) == 7

    signal_types = {
        signal.signal_type
        for signal in signals
    }

    assert "DNS_RESOLUTION_FAILED" in signal_types
    assert "INTERNET_UNREACHABLE" in signal_types

    finding_types = {
        finding.finding_type
        for finding in findings
    }

    assert "DNS_RESOLUTION_FAILURE" in finding_types
    assert "INTERNET_CONNECTIVITY_FAILURE" in finding_types


def test_network_pipeline_detects_unreachable_gateway():
    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
        "internet_reachable": False,
        "dns_working": False,
    }

    _, signals, findings = diagnose_network_evidence(evidence)

    assert any(
        signal.signal_type == "DEFAULT_GATEWAY_UNREACHABLE"
        for signal in signals
    )

    assert any(
        finding.finding_type == "LOCAL_NETWORK_UNREACHABLE"
        for finding in findings
    )


def test_network_pipeline_detects_disconnected_adapter():
    evidence = {
        "active_adapter": {
            "is_up": False,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": None,
        "gateway_reachable": False,
        "internet_reachable": False,
        "dns_working": False,
    }

    _, signals, findings = diagnose_network_evidence(evidence)

    assert any(
        signal.signal_type == "NETWORK_ADAPTER_DISCONNECTED"
        for signal in signals
    )

    assert any(
        finding.finding_type == "NETWORK_ADAPTER_DISCONNECTED"
        for finding in findings
    )


def test_network_pipeline_healthy_network_produces_no_failure_findings():
    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "internet_reachable": True,
        "dns_working": True,
    }

    _, signals, findings = diagnose_network_evidence(
        evidence
    )

    assert signals == []
    assert findings == []


def test_network_pipeline_preserves_signal_to_finding_relationship():
    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": True,
        "internet_reachable": False,
        "dns_working": False,
    }

    _, signals, findings = diagnose_network_evidence(
        evidence
    )

    dns_signal = next(
        signal
        for signal in signals
        if signal.signal_type == "DNS_RESOLUTION_FAILED"
    )

    dns_finding = next(
        finding
        for finding in findings
        if finding.finding_type == "DNS_RESOLUTION_FAILURE"
    )

    assert dns_finding.supporting_signals == [dns_signal]

from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
    NetworkDiagnosticCaseSynthesizer,
)


def test_network_diagnostic_pipeline_produces_coherent_case():
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    pipeline = NetworkDiagnosticPipeline()

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
        "dns_working": True,
        "internet_reachable": False,
    }

    case = synthesizer.synthesize(evidence)

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

def test_network_diagnostic_pipeline_produces_root_cause_confidence():
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    pipeline = NetworkDiagnosticPipeline()

    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
        "dns_working": True,
        "internet_reachable": False,
    }

    result = pipeline.diagnose(evidence)

    assert result["primary_cause"] is not None
    assert result["primary_cause"].cause_type == (
        "LOCAL_NETWORK_FAILURE"
    )

    assert len(result["confidences"]) == 1

    confidence = result["confidences"][0]

    assert confidence.subject == (
        "LOCAL_NETWORK_FAILURE"
    )
    assert confidence.level == "HIGH"

def test_network_diagnostic_case_preserves_confidence_identity():
    from engine.network_diagnostic_pipeline import (
        NetworkDiagnosticPipeline,
    )

    class CapturingPipeline(NetworkDiagnosticPipeline):

        def diagnose(self, evidence):
            result = super().diagnose(evidence)
            self.last_result = result
            return result

    pipeline = CapturingPipeline()

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    evidence = {
        "active_adapter": {
            "is_up": True,
            "addresses": [
                {
                    "type": "IPv4",
                    "address": "192.168.1.20",
                    "classification": "PRIVATE",
                }
            ],
        },
        "gateway": "192.168.1.1",
        "gateway_reachable": False,
        "dns_working": True,
        "internet_reachable": False,
    }

    case = synthesizer.synthesize(evidence)

    result = pipeline.last_result

    assert result["confidences"]
    assert case.confidences

    assert len(case.confidences) == len(
        result["confidences"]
    )

    for case_confidence, pipeline_confidence in zip(
        case.confidences,
        result["confidences"],
    ):
        assert case_confidence is pipeline_confidence

def test_network_pipeline_accepts_adaptive_gateway_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    observation = translator.translate(outcome)

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            observation
        )
    )

    signal = pipeline.signal_detector.detect(
        normalized_observation
    )

    assert signal is not None
    assert signal.signal_type == (
        "DEFAULT_GATEWAY_UNREACHABLE"
    )

def test_network_pipeline_normalizes_adaptive_gateway_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    assert normalized_observation.source == "network"
    assert normalized_observation.subject == (
        "network_gateway"
    )
    assert normalized_observation.attribute == (
        "reachable"
    )
    assert normalized_observation.value is False

def test_network_pipeline_normalizes_adaptive_dns_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_DNS_RESOLUTION",
        evidence={
            "dns_working": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    assert normalized_observation.source == "network"
    assert normalized_observation.subject == (
        "network_dns"
    )
    assert normalized_observation.attribute == "working"
    assert normalized_observation.value is False


def test_network_pipeline_normalizes_adaptive_internet_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_INTERNET_CONNECTIVITY",
        evidence={
            "internet_reachable": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    assert normalized_observation.source == "network"
    assert normalized_observation.subject == (
        "network_internet"
    )
    assert normalized_observation.attribute == (
        "reachable"
    )
    assert normalized_observation.value is False


def test_network_pipeline_normalizes_adaptive_adapter_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    adapters = [
        {
            "name": "Ethernet",
            "is_up": False,
        }
    ]

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": adapters,
        },
    )

    translator = DiagnosticOutcomeToObservation()

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observations = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    assert isinstance(
        normalized_observations,
        list,
    )

    assert len(normalized_observations) == 1

    normalized_observation = (
        normalized_observations[0]
    )

    assert normalized_observation.source == "network"
    assert normalized_observation.subject == (
        "network_adapter"
    )
    assert normalized_observation.attribute == (
        "is_up"
    )
    assert normalized_observation.value is False

def test_network_pipeline_normalized_adaptive_gateway_reaches_signal_engine():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence={
            "gateway_reachable": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    signal = pipeline.signal_detector.detect(
        normalized_observation
    )

    assert signal is not None
    assert signal.signal_type == (
        "DEFAULT_GATEWAY_UNREACHABLE"
    )

def test_network_pipeline_normalized_adaptive_dns_reaches_signal_engine():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_DNS_RESOLUTION",
        evidence={
            "dns_working": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    signal = pipeline.signal_detector.detect(
        normalized_observation
    )

    assert signal is not None
    assert signal.signal_type == (
        "DNS_RESOLUTION_FAILED"
    )


def test_network_pipeline_normalized_adaptive_internet_reaches_signal_engine():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_INTERNET_CONNECTIVITY",
        evidence={
            "internet_reachable": False,
        },
    )

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observation = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    signal = pipeline.signal_detector.detect(
        normalized_observation
    )

    assert signal is not None
    assert signal.signal_type == (
        "INTERNET_UNREACHABLE"
    )


def test_network_pipeline_normalized_adaptive_adapter_reaches_signal_engine():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    adapters = [
        {
            "name": "Ethernet",
            "is_up": True,
        },
        {
            "name": "Wi-Fi",
            "is_up": False,
        },
    ]

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": adapters,
        },
    )

    translator = DiagnosticOutcomeToObservation()

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observations = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    signals = []

    for observation in normalized_observations:
        signal = pipeline.signal_detector.detect(
            observation
        )

        if signal is not None:
            signals.append(signal)

    assert signals

    assert any(
        signal.signal_type
        == "NETWORK_ADAPTER_DISCONNECTED"
        for signal in signals
    )

def test_network_pipeline_normalizes_adaptive_adapter_collection():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    adapters = [
        {
            "name": "Ethernet",
            "is_up": True,
        },
        {
            "name": "Wi-Fi",
            "is_up": False,
        },
    ]

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": adapters,
        },
    )

    translator = DiagnosticOutcomeToObservation()

    adaptive_observation = translator.translate(
        outcome
    )

    pipeline = NetworkDiagnosticPipeline()

    normalized_observations = (
        pipeline.normalize_observation(
            adaptive_observation
        )
    )

    assert isinstance(
        normalized_observations,
        list,
    )

    assert len(normalized_observations) == 2

    assert (
        normalized_observations[0].source
        == "network"
    )
    assert (
        normalized_observations[0].subject
        == "network_adapter"
    )
    assert (
        normalized_observations[0].attribute
        == "is_up"
    )
    assert (
        normalized_observations[0].value
        is True
    )

    assert (
        normalized_observations[1].source
        == "network"
    )
    assert (
        normalized_observations[1].subject
        == "network_adapter"
    )
    assert (
        normalized_observations[1].attribute
        == "is_up"
    )
    assert (
        normalized_observations[1].value
        is False
    )

def test_network_pipeline_processes_adaptive_observations_into_reasoning():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

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

    pipeline = NetworkDiagnosticPipeline()

    gateway_result = pipeline.process_observation(
        gateway_observation
    )

    internet_result = pipeline.process_observation(
        internet_observation
    )

    observations = (
        gateway_result["observations"]
        + internet_result["observations"]
    )

    signals = (
        gateway_result["signals"]
        + internet_result["signals"]
    )

    findings = (
        gateway_result["findings"]
        + internet_result["findings"]
    )

    correlations = (
        gateway_result["correlations"]
        + internet_result["correlations"]
    )

    candidates = (
        gateway_result["candidates"]
        + internet_result["candidates"]
    )

    evaluations = (
        gateway_result["evaluations"]
        + internet_result["evaluations"]
    )

    confidences = (
        gateway_result["confidences"]
        + internet_result["confidences"]
    )

    assert observations
    assert signals
    assert findings
    assert correlations
    assert candidates
    assert evaluations
    assert confidences

    primary_causes = [
        result["primary_cause"]
        for result in (
            gateway_result,
            internet_result,
        )
        if result["primary_cause"] is not None
    ]

    assert primary_causes

    recommendations = [
        result["recommendation"]
        for result in (
            gateway_result,
            internet_result,
        )
        if result["recommendation"] is not None
    ]

    assert recommendations

def test_network_pipeline_accumulates_adaptive_observations_for_correlation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )
    from engine.diagnostic_action_outcome import (
        DiagnosticActionOutcome,
    )

    translator = DiagnosticOutcomeToObservation()

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

    pipeline = NetworkDiagnosticPipeline()

    gateway_result = pipeline.process_observation(
        gateway_observation
    )

    assert gateway_result["correlations"] == []

    internet_result = pipeline.process_observation(
        internet_observation
    )

    assert internet_result["observations"]

    assert internet_result["signals"]

    assert internet_result["findings"]

    assert internet_result["correlations"]

    assert any(
        correlation.correlation_type
        == "LOCAL_NETWORK_FAILURE"
        for correlation
        in internet_result["correlations"]
    )
