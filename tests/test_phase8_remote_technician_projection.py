from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_session import RemoteSession
from engine.remote_technician_projection import RemoteTechnicianProjection
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


def build_projection():
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

    case = DiagnosticCase()
    case.origin = "REMOTE"
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    case.session_id = session.session_id

    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    projection = RemoteTechnicianProjection(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    return (
        projection,
        machine,
        session,
        case,
        workflow,
        registry,
    )


def test_requires_remote_context():
    case = DiagnosticCase()
    case.origin = "REMOTE"

    try:
        RemoteTechnicianProjection(
            context=None,
            case=case,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for missing remote context."
        )


def test_requires_diagnostic_case():
    projection, *_ = build_projection()

    try:
        RemoteTechnicianProjection(
            context=projection.context,
            case=None,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for invalid case."
        )


def test_requires_remote_case_origin():
    projection, machine, session, *_ = build_projection()

    case = DiagnosticCase()

    context = RemoteRemediationContext(
        machine,
        session,
    )

    try:
        RemoteTechnicianProjection(
            context=context,
            case=case,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for non-remote case."
        )


def test_workflow_belongs_to_case():
    projection, machine, session, case, *_ = build_projection()

    other_case = DiagnosticCase()
    other_case.origin = "REMOTE"

    workflow = TechnicianWorkflow(other_case)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    try:
        RemoteTechnicianProjection(
            context=context,
            case=case,
            workflow=workflow,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for mismatched workflow."
        )


def test_engine_belongs_to_same_case_and_workflow():
    (
        projection,
        machine,
        session,
        case,
        workflow,
        registry,
    ) = build_projection()

    from engine.problem_solving_engine import (
        ProductionProblemSolvingEngine,
    )

    other_case = DiagnosticCase()
    other_case.origin = "REMOTE"

    other_workflow = TechnicianWorkflow(other_case)

    engine = ProductionProblemSolvingEngine(
        case=other_case,
        workflow=other_workflow,
        diagnostic_registry=registry,
    )

    context = RemoteRemediationContext(
        machine,
        session,
    )

    try:
        RemoteTechnicianProjection(
            context=context,
            case=case,
            workflow=workflow,
            diagnostic_registry=registry,
            engine=engine,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for mismatched engine."
        )


def test_exposes_remote_machine_identity():
    projection, machine, *_ = build_projection()

    assert projection.machine_id == machine.machine_id
    assert projection.hostname == machine.hostname
    assert projection.is_remote is True


def test_exposes_remote_session_identity():
    projection, _, session, *_ = build_projection()

    assert projection.session_id == session.session_id


def test_uses_canonical_production_engine():
    projection, *_ = build_projection()

    assert projection.engine.__class__.__name__ == (
        "ProductionProblemSolvingEngine"
    )


def test_projection_contains_canonical_projection():
    projection, *_ = build_projection()

    result = projection.projection()

    expected_keys = {
        "verification_result",
        "verification_complete",
        "recovery_cycle_count",
        "recovery_cycles",
        "current_recovery_cycle",
        "projection_schema_version",
        "case_id",
        "machine_id",
        "state",
        "workflow_state",
        "lifecycle_history",
        "action_required",
        "result",
        "failure",
        "domain_results",
        "domain_failures",
        "remediation_actions",
        "authorizations",
        "execution_available",
    }

    assert expected_keys.issubset(result.keys())


def test_projection_contains_remote_identity():
    projection, machine, session, case, *_ = build_projection()

    result = projection.projection()

    assert result["machine_id"] == machine.machine_id
    assert result["hostname"] == machine.hostname
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True
    assert result["case_id"] == case.case_id


def test_projection_uses_same_workflow_state():
    projection, *_ = build_projection()

    result = projection.projection()

    assert result["workflow_state"] == projection.workflow.state


def test_projection_uses_same_engine_state():
    projection, *_ = build_projection()

    result = projection.projection()

    assert result["state"] == projection.engine.state


def test_projection_does_not_create_second_workflow():
    projection, *_ = build_projection()

    assert projection.engine.workflow is projection.workflow


def test_projection_does_not_create_second_case():
    projection, *_ = build_projection()

    assert projection.engine.case is projection.case


def test_projection_is_defensive_copy():
    projection, *_ = build_projection()

    first = projection.projection()

    first["machine_id"] = "tampered"
    first["lifecycle_history"].append(
        {
            "from": "X",
            "to": "Y",
        }
    )

    second = projection.projection()

    assert second["machine_id"] != "tampered"
    assert len(second["lifecycle_history"]) == 0


def test_projection_does_not_mutate_engine():
    projection, *_ = build_projection()

    before = projection.engine.projection()

    projection.projection()

    after = projection.engine.projection()

    assert before == after


def test_remote_projection_preserves_canonical_projection_schema():
    projection, *_ = build_projection()

    result = projection.projection()

    assert result["projection_schema_version"] == "1.0"


def test_remote_projection_is_read_only_boundary():
    projection, *_ = build_projection()

    before_state = projection.engine.state
    before_workflow = projection.workflow.state

    projection.projection()

    assert projection.engine.state == before_state
    assert projection.workflow.state == before_workflow
