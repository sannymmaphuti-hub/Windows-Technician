from copy import deepcopy

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_authorization_boundary import RemoteAuthorizationBoundary
from engine.remote_case_integration import RemoteCaseIntegration
from engine.remote_decision_boundary import RemoteDecisionBoundary
from engine.remote_failure_recovery import RemoteFailureRecovery
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_execution import RemoteRemediationExecution
from engine.remote_session import RemoteSession
from engine.remote_technician_operations import RemoteTechnicianOperations
from engine.remote_technician_projection import RemoteTechnicianProjection
from engine.remote_verification import RemoteVerification
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


def build_remote_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine,
        session,
    )

    return machine, session, context


def build_remote_case():
    machine, session, context = build_remote_context()

    case = DiagnosticCase()
    case.origin = "REMOTE"
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    case.session_id = session.session_id

    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    return (
        machine,
        session,
        context,
        case,
        workflow,
        registry,
        engine,
    )


def test_remote_case_is_canonical_case():
    (
        _machine,
        _session,
        _context,
        case,
        workflow,
        _registry,
        engine,
    ) = build_remote_case()

    assert engine.case is case
    assert workflow.case is case


def test_remote_components_share_canonical_workflow():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    decision = RemoteDecisionBoundary(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    authorization = RemoteAuthorizationBoundary(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    verification = RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    assert decision.engine is not engine
    assert authorization.engine is not engine

    assert decision.workflow is workflow
    assert authorization.workflow is workflow
    assert verification.workflow is workflow
    assert recovery.workflow is workflow


def test_remote_boundaries_can_share_one_explicit_engine():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    verification = RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    assert verification.engine is engine
    assert recovery.engine is engine
    assert projection.engine is engine


def test_remote_operation_does_not_create_second_case():
    machine, session, _context = build_remote_context()

    operations = RemoteTechnicianOperations(
        machine=machine,
        session=session,
    )

    case = operations.diagnose([])

    assert operations.case is case
    assert case.origin == "REMOTE"


def test_remote_case_integration_uses_same_case():
    (
        _machine,
        _session,
        _context,
        case,
        _workflow,
        _registry,
        _engine,
    ) = build_remote_case()

    integration = RemoteCaseIntegration(case)

    assert integration.case is case
    assert integration.workflow.case is case


def test_remote_projection_is_only_a_projection():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    before_state = engine.state
    before_workflow_state = workflow.state
    before_case_id = case.case_id

    result = projection.projection()

    assert result["case_id"] == before_case_id
    assert engine.state == before_state
    assert workflow.state == before_workflow_state
    assert projection.case is case
    assert projection.workflow is workflow
    assert projection.engine is engine


def test_remote_projection_cannot_mutate_canonical_projection():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    first = projection.projection()
    first["machine_id"] = "tampered"
    first["remediation_actions"] = {"tampered": "value"}

    second = projection.projection()

    assert second["machine_id"] == case.machine_id
    assert second["remediation_actions"] != {
        "tampered": "value"
    }


def test_remote_remediation_execution_requires_available_machine():
    (
        _machine,
        session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    execution = RemoteRemediationExecution(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    # ManagedMachine.is_available is a read-only property.
    # Availability is controlled by the canonical connection state.
    session.disconnect()

    with pytest.raises(ValueError):
        execution.execute("unknown-action")


def test_remote_remediation_execution_delegates_to_canonical_engine(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    execution = RemoteRemediationExecution(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    sentinel = object()
    calls = []

    def fake_execute(action_id, expected=None, observed=None):
        calls.append(
            (action_id, expected, observed)
        )
        return sentinel

    monkeypatch.setattr(
        engine,
        "execute_remediation",
        fake_execute,
    )

    result = execution.execute(
        "action-001",
        expected="expected",
        observed="observed",
    )

    assert result is sentinel
    assert calls == [
        (
            "action-001",
            "expected",
            "observed",
        )
    ]


def test_remote_verification_delegates_to_canonical_engine(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    verification = RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    sentinel = {
        "verified": True,
    }

    calls = []

    def fake_verify(
        result=None,
        expected=None,
        observed=None,
    ):
        calls.append(
            (
                result,
                expected,
                observed,
            )
        )
        return sentinel

    monkeypatch.setattr(
        engine,
        "verify_remediation",
        fake_verify,
    )

    result = verification.verify(
        result="result",
        expected="expected",
        observed="observed",
    )

    assert result == sentinel
    assert calls == [
        (
            "result",
            "expected",
            "observed",
        )
    ]


def test_remote_verification_does_not_execute_remediation(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    verification = RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    verify_calls = []
    execute_calls = []

    def fake_verify(*args, **kwargs):
        verify_calls.append(True)
        return {"verified": True}

    def fake_execute(*args, **kwargs):
        execute_calls.append(True)
        return object()

    monkeypatch.setattr(
        engine,
        "verify_remediation",
        fake_verify,
    )

    monkeypatch.setattr(
        engine,
        "execute_remediation",
        fake_execute,
    )

    verification.verify(
        result="result",
        expected="expected",
        observed="observed",
    )

    assert verify_calls == [True]
    assert execute_calls == []


def test_remote_recovery_delegates_to_canonical_engine(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    calls = []

    def fake_recovery():
        calls.append(True)
        return "recovery-cycle"

    monkeypatch.setattr(
        engine,
        "start_recovery_cycle",
        fake_recovery,
    )

    result = recovery.start_recovery_cycle()

    assert result == "recovery-cycle"
    assert calls == [True]


def test_remote_recovery_does_not_execute_remediation(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    recovery_calls = []
    execute_calls = []

    def fake_recovery():
        recovery_calls.append(True)
        return "cycle"

    def fake_execute(*args, **kwargs):
        execute_calls.append(True)
        return object()

    monkeypatch.setattr(
        engine,
        "start_recovery_cycle",
        fake_recovery,
    )

    monkeypatch.setattr(
        engine,
        "execute_remediation",
        fake_execute,
    )

    recovery.start_recovery_cycle()

    assert recovery_calls == [True]
    assert execute_calls == []


def test_remote_recovery_does_not_automatically_diagnose(
    monkeypatch,
):
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    recovery_calls = []
    diagnostic_calls = []

    def fake_recovery():
        recovery_calls.append(True)
        return "cycle"

    def fake_execute_domains(*args, **kwargs):
        diagnostic_calls.append(True)
        return object()

    monkeypatch.setattr(
        engine,
        "start_recovery_cycle",
        fake_recovery,
    )

    monkeypatch.setattr(
        engine,
        "execute_domains",
        fake_execute_domains,
    )

    recovery.start_recovery_cycle()

    assert recovery_calls == [True]
    assert diagnostic_calls == []


def test_remote_authorization_does_not_execute_remediation(
    monkeypatch,
):
    (
        _machine,
        _session,
        _context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    authorization = RemoteAuthorizationBoundary(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    execute_calls = []

    def fake_execute(*args, **kwargs):
        execute_calls.append(True)
        return object()

    monkeypatch.setattr(
        authorization.engine,
        "execute_remediation",
        fake_execute,
    )

    # Preparing authorization is deliberately non-executing.
    monkeypatch.setattr(
        authorization.engine,
        "prepare_remediation_authorization",
        lambda: {},
    )

    authorization.prepare()

    assert execute_calls == []


def test_remote_identity_is_preserved_across_projection():
    (
        machine,
        session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    result = projection.projection()

    assert result["machine_id"] == machine.machine_id
    assert result["hostname"] == machine.hostname
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True


def test_remote_components_do_not_create_parallel_lifecycle():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    verification = RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    recovery = RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    assert verification.case is case
    assert recovery.case is case
    assert projection.case is case

    assert verification.workflow is workflow
    assert recovery.workflow is workflow
    assert projection.workflow is workflow

    assert verification.engine is engine
    assert recovery.engine is engine
    assert projection.engine is engine


def test_remote_boundary_does_not_mutate_case():
    (
        _machine,
        _session,
        context,
        case,
        workflow,
        registry,
        engine,
    ) = build_remote_case()

    before = deepcopy(case.__dict__)

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )

    projection.projection()

    assert case.__dict__ == before
