# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC PIPELINE INTEGRATION
# ==========================================

import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal
from engine.finding_engine import FindingEngine
from engine.network_adapter_finding_rule import NetworkAdapterFindingRule
from engine.local_network_unreachable_rule import LocalNetworkUnreachableRule
from engine.dns_resolution_failure_rule import DNSResolutionFailureRule
from engine.internet_connectivity_failure_rule import (
    InternetConnectivityFailureRule,
)
from engine.correlation_engine import CorrelationEngine
from engine.network_adapter_correlation_rule import (
    NetworkAdapterCorrelationRule,
)
from engine.local_network_failure_correlation_rule import (
    LocalNetworkFailureCorrelationRule,
)
from engine.root_cause_engine import RootCauseEngine
from engine.dns_failure_root_cause_rule import DNSFailureRootCauseRule
from engine.local_network_failure_root_cause_rule import (
    LocalNetworkFailureRootCauseRule,
)
from engine.network_adapter_failure_root_cause_rule import (
    NetworkAdapterFailureRootCauseRule,
)
from engine.root_cause_evaluation_engine import RootCauseEvaluationEngine
from engine.dns_failure_evaluation_rule import DNSFailureEvaluationRule
from engine.local_network_failure_evaluation_rule import (
    LocalNetworkFailureEvaluationRule,
)
from engine.network_adapter_failure_evaluation_rule import (
    NetworkAdapterFailureEvaluationRule,
)
from engine.root_cause_selection import RootCauseSelection
from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)
from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline


def build_pipeline():
    finding_engine = FindingEngine()

    finding_engine.register_rule(
        NetworkAdapterFindingRule()
    )
    finding_engine.register_rule(
        LocalNetworkUnreachableRule()
    )
    finding_engine.register_rule(
        DNSResolutionFailureRule()
    )
    finding_engine.register_rule(
        InternetConnectivityFailureRule()
    )

    correlation_engine = CorrelationEngine()

    correlation_engine.register_rule(
        NetworkAdapterCorrelationRule()
    )
    correlation_engine.register_rule(
        LocalNetworkFailureCorrelationRule()
    )

    root_cause_engine = RootCauseEngine()

    root_cause_engine.register_rule(
        DNSFailureRootCauseRule()
    )
    root_cause_engine.register_rule(
        LocalNetworkFailureRootCauseRule()
    )
    root_cause_engine.register_rule(
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

    confidence_engine = ConfidenceEngine()

    confidence_engine.register_rule(
        RootCauseConfidenceRule()
    )

    return RemoteDiagnosticPipeline(
        signal_detector=ObservationToSignal(),
        finding_engine=finding_engine,
        correlation_engine=correlation_engine,
        root_cause_engine=root_cause_engine,
        root_cause_evaluation_engine=evaluation_engine,
        root_cause_selection=RootCauseSelection(),
        recommendation_orchestrator=(
            NetworkRecommendationOrchestrator()
        ),
        confidence_engine=confidence_engine,
    )


def build_remote_input(observations):
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine,
        session,
    )

    return RemoteDiagnosticInput(
        context,
        observations,
    )


def test_remote_pipeline_requires_remote_input():
    pipeline = build_pipeline()

    with pytest.raises(ValueError):
        pipeline.diagnose(None)


def test_remote_pipeline_accepts_remote_diagnostic_input():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert isinstance(result, dict)


def test_remote_pipeline_preserves_remote_identity():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert result["machine_id"] == "machine-001"
    assert result["hostname"] == "REMOTE-PC"
    assert result["session_id"] == remote_input.session_id
    assert result["is_remote"] is True


def test_remote_pipeline_uses_supplied_observations():
    pipeline = build_pipeline()

    observation = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=False,
    )

    remote_input = build_remote_input([observation])

    result = pipeline.diagnose(remote_input)

    assert result["observations"] == [observation]


def test_remote_pipeline_produces_signals_from_observations():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert len(result["signals"]) > 0


def test_remote_pipeline_produces_findings():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert len(result["findings"]) > 0


def test_remote_pipeline_preserves_machine_context_in_result():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert result["machine_id"] == (
        remote_input.machine_id
    )

    assert result["session_id"] == (
        remote_input.session_id
    )


def test_remote_pipeline_does_not_create_workflow():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert "workflow" not in result
    assert "technician_workflow" not in result


def test_remote_pipeline_does_not_execute_remediation():
    pipeline = build_pipeline()

    remote_input = build_remote_input(
        [
            Observation(
                source="network",
                subject="network_gateway",
                attribute="reachable",
                value=False,
            )
        ]
    )

    result = pipeline.diagnose(remote_input)

    assert "remediation_operation" not in result
    assert "execution_status" not in result


def test_remote_pipeline_rejects_wrong_input_type():
    pipeline = build_pipeline()

    with pytest.raises(ValueError):
        pipeline.diagnose([])


def test_remote_pipeline_rejects_empty_observations():
    pipeline = build_pipeline()

    remote_input = build_remote_input([])

    result = pipeline.diagnose(remote_input)

    assert result["observations"] == []
    assert result["signals"] == []
    assert result["findings"] == []


def test_remote_pipeline_does_not_mutate_input_observations():
    pipeline = build_pipeline()

    observations = [
        Observation(
            source="network",
            subject="network_gateway",
            attribute="reachable",
            value=False,
        )
    ]

    remote_input = build_remote_input(observations)

    original = list(remote_input.observations)

    pipeline.diagnose(remote_input)

    assert remote_input.observations == original
    