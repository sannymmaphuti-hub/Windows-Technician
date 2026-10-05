# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC CASE INTEGRATION TESTS
# ==========================================

import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.observation import Observation
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)

def build_remote_input():
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

    observations = [
        Observation(
            source="remote",
            subject="network",
            attribute="adapter_status",
            value="disconnected",
        ),
    ]

    return RemoteDiagnosticInput(
        context,
        observations,
    )


def build_case_from_result(result):
    case = DiagnosticCase()

    case.observations.extend(
        result["observations"]
    )

    case.signals.extend(
        result["signals"]
    )

    case.findings.extend(
        result["findings"]
    )

    case.correlations.extend(
        result["correlations"]
    )

    case.root_causes.extend(
        result["candidates"]
    )

    if result["recommendation"] is not None:
        case.recommendations.append(
            result["recommendation"]
        )

    return case


def test_remote_diagnostic_result_can_become_diagnostic_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert isinstance(case, DiagnosticCase)


def test_remote_observations_are_preserved_in_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert case.observations == result["observations"]


def test_remote_signals_are_preserved_in_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert case.signals == result["signals"]


def test_remote_findings_are_preserved_in_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert case.findings == result["findings"]


def test_remote_root_causes_are_preserved_in_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert case.root_causes == result["candidates"]


def test_remote_recommendation_is_preserved_in_case():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    if result["recommendation"] is None:
        assert case.recommendations == []
    else:
        assert case.recommendations == [
            result["recommendation"]
        ]


def test_remote_machine_identity_is_preserved_with_case_context():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    case.machine_id = result["machine_id"]
    case.hostname = result["hostname"]
    case.session_id = result["session_id"]

    assert case.machine_id == "machine-001"
    assert case.hostname == "REMOTE-PC"
    assert case.session_id == remote_input.session_id


def test_remote_case_can_enter_existing_technician_workflow():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert workflow.state.value == "OPEN"


def test_remote_case_uses_existing_workflow():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    workflow = TechnicianWorkflow(case)

    assert isinstance(
        workflow,
        TechnicianWorkflow,
    )


def test_remote_diagnostic_does_not_authorize_remediation():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert "remediation_actions" not in result


def test_remote_diagnostic_does_not_execute_remediation():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert "execution_status" not in result
    assert "remediation_result" not in result


def test_remote_case_is_not_a_remote_specific_case_type():
    remote_input = build_remote_input()

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    case = build_case_from_result(result)

    assert type(case) is DiagnosticCase