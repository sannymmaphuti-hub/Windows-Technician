from engine.finding import Finding
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_pipeline import RootCauseEvaluationPipeline
from engine.root_cause_selection import RootCauseSelection
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine

def create_engine():
    engine = RootCauseEngine()

    engine.register_rule(DNSFailureRootCauseRule())
    engine.register_rule(LocalNetworkFailureRootCauseRule())
    engine.register_rule(NetworkAdapterFailureRootCauseRule())

    return engine


def create_dns_finding():
    return Finding(
        finding_type="DNS_RESOLUTION_FAILURE",
        category="NETWORK",
        severity="MEDIUM",
        description="DNS resolution is failing.",
    )


def create_local_network_finding():
    return Finding(
        finding_type="LOCAL_NETWORK_UNREACHABLE",
        category="NETWORK",
        severity="HIGH",
        description="The local network gateway is unreachable.",
    )


def create_adapter_finding():
    return Finding(
        finding_type="NETWORK_ADAPTER_DISCONNECTED",
        category="NETWORK",
        severity="HIGH",
        description="The network adapter is disconnected.",
    )


def create_internet_finding():
    return Finding(
        finding_type="INTERNET_CONNECTIVITY_FAILURE",
        category="NETWORK",
        severity="HIGH",
        description="Internet connectivity is unavailable.",
    )


def test_network_root_cause_engine_can_be_created():
    engine = create_engine()

    assert engine is not None


def test_dns_failure_can_produce_network_root_cause_candidate():
    engine = create_engine()

    findings = [create_dns_finding()]

    candidates = engine.detect(findings)

    assert any(
        candidate.category == "NETWORK"
        for candidate in candidates
    )


def test_local_network_failure_can_produce_network_root_cause_candidate():
    engine = create_engine()

    findings = [
        create_local_network_finding(),
        create_internet_finding(),
    ]

    candidates = engine.detect(findings)

    assert any(
        candidate.category == "NETWORK"
        for candidate in candidates
    )


def test_adapter_failure_can_produce_network_root_cause_candidate():
    engine = create_engine()

    findings = [create_adapter_finding()]

    candidates = engine.detect(findings)

    assert any(
        candidate.category == "NETWORK"
        for candidate in candidates
    )


def test_internet_failure_alone_does_not_prove_specific_root_cause():
    engine = create_engine()

    findings = [create_internet_finding()]

    candidates = engine.detect(findings)

    assert candidates == []


def test_network_root_cause_evaluation_pipeline_can_evaluate_candidates():
    engine = create_engine()

    findings = [
        create_local_network_finding(),
        create_internet_finding(),
    ]

    candidates = engine.detect(findings)

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

    pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    evaluations = pipeline.evaluate(
        candidates,
        findings,
    )

    assert evaluations

    assert evaluations[0].candidate.cause_type == (
        "LOCAL_NETWORK_FAILURE"
    )

    assert evaluations[0].assessment == (
        "STRONGLY_SUPPORTED"
    )

def test_network_root_cause_selection_does_not_select_insufficient_evidence():
    selection = RootCauseSelection()

    result = selection.select([])

    assert result is None