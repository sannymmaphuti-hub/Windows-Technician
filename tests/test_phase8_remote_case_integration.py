# ==========================================
# Windows Technician V1.0
# PHASE 8.4 REMOTE CASE INTEGRATION
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.observation import Observation
from engine.remote_case_integration import (
    RemoteCaseIntegration,
)
from engine.remote_session import RemoteSession
from engine.remote_technician_operations import (
    RemoteTechnicianOperations,
)
from engine.remote_diagnostic_execution import (
    RemoteDiagnosticExecution,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
)


def build_case():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    operations = RemoteTechnicianOperations(
        machine,
        session,
    )

    execution = RemoteDiagnosticExecution(
        operations
    )

    return execution.execute(
        [
            Observation(
                source="remote",
                subject="network",
                attribute="adapter_status",
                value="disconnected",
            )
        ]
    )


def test_requires_canonical_case():
    with pytest.raises(ValueError):
        RemoteCaseIntegration(object())


def test_requires_remote_origin():
    case = DiagnosticCase()

    with pytest.raises(ValueError):
        RemoteCaseIntegration(case)


def test_creates_canonical_technician_workflow():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert isinstance(
        integration.workflow,
        TechnicianWorkflow,
    )


def test_workflow_references_same_case():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert integration.workflow.case is case


def test_remote_case_identity_is_preserved():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert (
        integration.machine_id
        == case.machine_id
    )

    assert (
        integration.hostname
        == case.hostname
    )

    assert (
        integration.session_id
        == case.session_id
    )


def test_case_starts_open():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert (
        integration.lifecycle_state
        == "OPEN"
    )


def test_remote_case_enters_investigation():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    workflow = integration.start_investigation()

    assert workflow.state.value == "INVESTIGATING"


def test_investigation_uses_existing_workflow():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert type(integration.workflow) is TechnicianWorkflow


def test_remote_case_does_not_create_remote_workflow():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert type(integration.workflow) is not type(
        "RemoteTechnicianWorkflow"
    )


def test_case_identity_remains_stable_after_investigation():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    original_case_id = case.case_id

    integration.start_investigation()

    assert case.case_id == original_case_id
    assert case.origin == "REMOTE"


def test_integration_has_no_remediation_authorization():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert not hasattr(
        integration,
        "authorize_remediation",
    )


def test_integration_has_no_remediation_execution():
    case = build_case()

    integration = RemoteCaseIntegration(
        case
    )

    assert not hasattr(
        integration,
        "execute_remediation",
    )
