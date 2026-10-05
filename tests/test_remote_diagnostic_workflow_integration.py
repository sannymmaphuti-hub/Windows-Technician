# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC WORKFLOW INTEGRATION TESTS
# ==========================================

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


def build_remote_case():
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

    remote_input = RemoteDiagnosticInput(
        context,
        observations,
    )

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

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

    return case, machine, session


def test_remote_case_starts_in_open_state():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    assert workflow.state == WorkflowState.OPEN


def test_remote_case_enters_investigating_state():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state == WorkflowState.INVESTIGATING


def test_remote_case_can_enter_existing_workflow():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state == WorkflowState.INVESTIGATING


def test_remote_workflow_preserves_case_identity():
    case, machine, session = build_remote_case()

    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert machine.machine_id == "machine-001"
    assert machine.hostname == "REMOTE-PC"
    assert session.machine is machine


def test_remote_workflow_preserves_diagnostic_observations():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    assert workflow.case.observations


def test_remote_workflow_preserves_diagnostic_collections():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    assert isinstance(
        workflow.case.signals,
        list,
    )

    assert isinstance(
        workflow.case.findings,
        list,
    )

    assert isinstance(
        workflow.case.correlations,
        list,
    )


def test_remote_workflow_history_records_investigation():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert len(workflow.history) == 1

    previous_state, new_state = workflow.history[-1]

    assert previous_state == WorkflowState.OPEN
    assert new_state == WorkflowState.INVESTIGATING


def test_remote_workflow_history_uses_existing_transition_contract():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert all(
        isinstance(transition, tuple)
        and len(transition) == 2
        for transition in workflow.history
    )


def test_remote_diagnosis_does_not_start_remediation():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state == WorkflowState.INVESTIGATING
    assert workflow.state != WorkflowState.REMEDIATING


def test_remote_workflow_does_not_execute_remediation():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state != WorkflowState.REMEDIATING
    assert not hasattr(
        workflow,
        "execute_remediation",
    )


def test_remote_case_uses_existing_technician_workflow():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    assert isinstance(
        workflow,
        TechnicianWorkflow,
    )


def test_remote_workflow_has_no_separate_lifecycle():
    case, _, _ = build_remote_case()

    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.state in {
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
        WorkflowState.DIAGNOSED,
        WorkflowState.ACTION_REQUIRED,
        WorkflowState.REMEDIATING,
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
        WorkflowState.ESCALATED,
    }