from engine.confidence_engine import ConfidenceEngine
from engine.correlation_engine import CorrelationEngine
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.finding_engine import FindingEngine
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.network_adapter_finding_rule import (
    NetworkAdapterFindingRule,
)
from engine.local_network_unreachable_rule import (
    LocalNetworkUnreachableRule,
)
from engine.dns_resolution_failure_rule import (
    DNSResolutionFailureRule,
)
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.root_cause_reasoning import RootCauseReasoning
from engine.root_cause_selection import RootCauseSelection
from engine.signal import Signal
from engine.finding import Finding


def create_root_cause_reasoning():
    candidate_engine = RootCauseEngine()

    candidate_engine.register_rule(
        DNSFailureRootCauseRule()
    )
    candidate_engine.register_rule(
        LocalNetworkFailureRootCauseRule()
    )
    candidate_engine.register_rule(
        NetworkAdapterFailureRootCauseRule()
    )

    evaluation_engine = RootCauseEvaluationEngine()

    evaluation_engine.register_rule(
        DNSFailureEvaluationRule()
    )
    evaluation_engine.register_rule(
        LocalNetworkFailureEvaluationRule()
    )
    evaluation_engine.register_rule(
        NetworkAdapterFailureEvaluationRule()
    )

    evaluation_pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    return RootCauseReasoning(
        candidate_engine=candidate_engine,
        evaluation_pipeline=evaluation_pipeline,
        selection=RootCauseSelection(),
        confidence_engine=ConfidenceEngine(),
    )


def create_finding_engine():
    engine = FindingEngine()

    engine.register_rule(
        NetworkAdapterFindingRule()
    )
    engine.register_rule(
        LocalNetworkUnreachableRule()
    )
    engine.register_rule(
        DNSResolutionFailureRule()
    )
    engine.register_rule(
        InternetConnectivityFailureRule()
    )

    return engine


def dns_failure_findings():
    signal = Signal(
        signal_type="DNS_RESOLUTION_FAILED",
        source="network",
        subject="network_dns",
        attribute="working",
        value=False,
    )

    return create_finding_engine().detect(signal)


def local_network_failure_findings():
    gateway_signal = Signal(
        signal_type="DEFAULT_GATEWAY_UNREACHABLE",
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=False,
    )

    internet_signal = Signal(
        signal_type="INTERNET_UNREACHABLE",
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=False,
    )

    engine = create_finding_engine()

    findings = []
    findings.extend(
        engine.detect(gateway_signal)
    )
    findings.extend(
        engine.detect(internet_signal)
    )

    return findings


def adapter_failure_findings():
    signal = Signal(
        signal_type="NETWORK_ADAPTER_DISCONNECTED",
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    return create_finding_engine().detect(signal)


def test_dns_root_cause_reasoning_produces_established_cause():

    result = create_root_cause_reasoning().analyze(
        dns_failure_findings()
    )

    assert result["primary_cause"] is not None
    assert result["primary_cause"].cause_type == "DNS_FAILURE"


def test_local_network_root_cause_reasoning_produces_established_cause():

    result = create_root_cause_reasoning().analyze(
        local_network_failure_findings()
    )

    assert result["primary_cause"] is not None
    assert (
        result["primary_cause"].cause_type
        == "LOCAL_NETWORK_FAILURE"
    )


def test_adapter_root_cause_reasoning_produces_established_cause():

    result = create_root_cause_reasoning().analyze(
        adapter_failure_findings()
    )

    assert result["primary_cause"] is not None
    assert (
        result["primary_cause"].cause_type
        == "NETWORK_ADAPTER_FAILURE"
    )


def test_internet_failure_alone_has_no_established_root_cause():

    signal = Signal(
        signal_type="INTERNET_UNREACHABLE",
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=False,
    )

    findings = create_finding_engine().detect(
        signal
    )

    result = create_root_cause_reasoning().analyze(
        findings
    )

    assert result["primary_cause"] is None


def test_reasoning_result_exposes_recommendation_input():

    result = create_root_cause_reasoning().analyze(
        dns_failure_findings()
    )

    assert "primary_cause" in result
    assert "evaluations" in result
    assert "confidences" in result