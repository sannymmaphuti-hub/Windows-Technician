from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_execution import (
    RemoteRemediationExecution,
)
from engine.remote_session import RemoteSession
from engine.managed_machine import ManagedMachine
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


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


def build_execution():
    case = build_case()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()
    context = build_context()

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    return RemoteRemediationExecution(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )


def test_requires_remote_context():
    case = build_case()

    try:
        RemoteRemediationExecution(
            context="not-context",
            case=case,
        )
    except ValueError:
        return

    assert False


def test_requires_remote_case():
    context = build_context()

    try:
        RemoteRemediationExecution(
            context=context,
            case=DiagnosticCase(),
        )
    except ValueError:
        return

    assert False


def test_creates_canonical_engine():
    execution = build_execution()

    assert type(execution.engine) is ProductionProblemSolvingEngine


def test_engine_uses_same_case():
    execution = build_execution()

    assert execution.engine.case is execution.case


def test_engine_uses_same_workflow():
    execution = build_execution()

    assert execution.engine.workflow is execution.workflow


def test_preserves_remote_identity():
    execution = build_execution()

    assert execution.machine_id == "machine-001"
    assert execution.hostname == "REMOTE-PC"
    assert execution.is_remote is True


def test_session_identity_is_preserved():
    execution = build_execution()

    assert execution.session_id == (
        execution.context.session_id
    )


def test_execution_delegates_to_canonical_engine():
    execution = build_execution()

    sentinel = object()

    execution.engine.execute_remediation = (
        lambda action_id, expected=None, observed=None: sentinel
    )

    result = execution.execute(
        "action-001",
        expected="expected",
        observed="observed",
    )

    assert result is sentinel


def test_execution_stores_result():
    execution = build_execution()

    class Result:
        execution_status = "EXECUTED"

    result = Result()

    execution.engine.execute_remediation = (
        lambda action_id, expected=None, observed=None: result
    )

    returned = execution.execute("action-001")

    assert returned is result
    assert execution.result is not result
    assert execution.result.execution_status == "EXECUTED"


def test_unavailable_machine_blocks_execution():
    execution = build_execution()

    execution.context.machine.connection_state = "DISCONNECTED"

    called = []

    execution.engine.execute_remediation = (
        lambda *args, **kwargs: called.append(True)
    )

    try:
        execution.execute("action-001")
    except ValueError:
        pass
    else:
        assert False

    assert called == []


def test_does_not_authorize():
    execution = build_execution()

    assert not hasattr(
        execution,
        "authorize_remediation",
    )


def test_does_not_bind_operation():
    execution = build_execution()

    assert not hasattr(
        execution,
        "bind_operation",
    )


def test_does_not_verify():
    execution = build_execution()

    assert not hasattr(
        execution,
        "verify_remediation",
    )


def test_does_not_create_second_workflow():
    execution = build_execution()

    assert execution.engine.workflow is execution.workflow


def test_remote_context_remains_execution_context():
    execution = build_execution()

    assert execution.context.is_remote is True
    assert execution.is_remote is True
