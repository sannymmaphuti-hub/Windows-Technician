from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_failure_recovery import RemoteFailureRecovery
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_session import RemoteSession
from engine.managed_machine import ManagedMachine
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle


def build_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    return RemoteRemediationContext(
        machine,
        session,
    )


def build_case():
    case = DiagnosticCase()
    case.origin = "REMOTE"
    case.machine_id = "machine-001"
    case.hostname = "REMOTE-PC"
    case.session_id = "session-001"

    return case


def build_recovery():
    case = build_case()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()
    context = build_context()

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    return RemoteFailureRecovery(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )


def move_to_remediating(recovery):
    recovery.workflow.start_investigation()
    recovery.workflow.mark_diagnosed()
    recovery.workflow.require_action()
    recovery.workflow.start_remediation()


def test_requires_remote_context():
    case = build_case()

    try:
        RemoteFailureRecovery(
            context="invalid",
            case=case,
        )
    except ValueError:
        return

    assert False


def test_requires_remote_case():
    context = build_context()

    try:
        RemoteFailureRecovery(
            context=context,
            case=DiagnosticCase(),
        )
    except ValueError:
        return

    assert False


def test_creates_canonical_production_engine():
    recovery = build_recovery()

    assert type(recovery.engine) is ProductionProblemSolvingEngine


def test_engine_uses_same_case():
    recovery = build_recovery()

    assert recovery.engine.case is recovery.case


def test_engine_uses_same_workflow():
    recovery = build_recovery()

    assert recovery.engine.workflow is recovery.workflow


def test_preserves_remote_identity():
    recovery = build_recovery()

    assert recovery.machine_id == "machine-001"
    assert recovery.hostname == "REMOTE-PC"
    assert recovery.session_id == (
        recovery.context.session_id
    )
    assert recovery.is_remote is True


def test_recovery_requires_remediating_workflow():
    recovery = build_recovery()

    try:
        recovery.start_recovery_cycle()
    except ValueError:
        return

    assert False


def test_recovery_delegates_to_canonical_engine():
    recovery = build_recovery()

    move_to_remediating(recovery)

    sentinel = object()

    recovery.engine.start_recovery_cycle = (
        lambda: sentinel
    )

    result = recovery.start_recovery_cycle()

    assert result is sentinel


def test_recovery_creates_canonical_cycle():
    recovery = build_recovery()

    move_to_remediating(recovery)

    cycle = recovery.start_recovery_cycle()

    assert isinstance(
        cycle,
        TechnicianRecoveryCycle,
    )


def test_recovery_cycle_is_recorded_by_canonical_history():
    recovery = build_recovery()

    move_to_remediating(recovery)

    cycle = recovery.start_recovery_cycle()

    assert recovery.recovery_cycle_count == 2
    assert (
        recovery.engine.recovery_history.latest_cycle
        is cycle
    )


def test_recovery_enters_investigation():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert recovery.workflow.state.value == "INVESTIGATING"


def test_recovery_does_not_execute_remediation():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert not hasattr(
        recovery,
        "execute_remediation",
    )


def test_recovery_does_not_authorize_remediation():
    recovery = build_recovery()

    assert not hasattr(
        recovery,
        "authorize_remediation",
    )


def test_recovery_does_not_retry():
    recovery = build_recovery()

    assert not hasattr(
        recovery,
        "retry",
    )


def test_recovery_does_not_create_second_workflow():
    recovery = build_recovery()

    assert recovery.engine.workflow is recovery.workflow


def test_recovery_preserves_machine_identity():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert recovery.machine_id == "machine-001"
    assert recovery.case.machine_id == "machine-001"


def test_recovery_preserves_session_identity():
    recovery = build_recovery()

    session_id = recovery.session_id

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert recovery.session_id == session_id


def test_recovery_does_not_automatically_diagnose():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert recovery.workflow.state.value == "INVESTIGATING"


def test_recovery_projection_preserves_remote_identity():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    projection = recovery.projection()

    assert projection["machine_id"] == "machine-001"
    assert projection["hostname"] == "REMOTE-PC"
    assert projection["session_id"] == recovery.session_id
    assert projection["is_remote"] is True


def test_recovery_projection_uses_canonical_history():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    projection = recovery.projection()

    assert projection["recovery_cycle_count"] == 2
    assert len(projection["recovery_cycles"]) == 2


def test_recovery_is_explicit():
    recovery = build_recovery()

    move_to_remediating(recovery)

    assert recovery.recovery_cycle_count == 1

    # Merely reaching REMEDIATING does not create a cycle.
    assert recovery.workflow.state.value == "REMEDIATING"


def test_recovery_does_not_duplicate_cycle():
    recovery = build_recovery()

    move_to_remediating(recovery)

    recovery.start_recovery_cycle()

    assert recovery.recovery_cycle_count == 2
    assert recovery.engine.recovery_history.cycle_count == 2


def test_recovery_cycle_has_recovery_identity():
    recovery = build_recovery()

    move_to_remediating(recovery)

    cycle = recovery.start_recovery_cycle()

    assert cycle.is_recovery is True
    assert cycle.is_original is False


def test_recovery_cycle_numbers_are_sequential():
    recovery = build_recovery()

    move_to_remediating(recovery)

    cycle = recovery.start_recovery_cycle()

    assert cycle.cycle_number == 1
    assert recovery.current_recovery_cycle.cycle_number == 1
