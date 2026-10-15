from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_session import RemoteSession
from engine.remote_verification import RemoteVerification
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


def build_verification():
    case = build_case()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()
    context = build_context()

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )

    return RemoteVerification(
        context=context,
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
        engine=engine,
    )


def test_requires_remote_context():
    case = build_case()

    try:
        RemoteVerification(
            context="not-context",
            case=case,
        )
    except ValueError:
        return

    assert False


def test_requires_remote_case():
    context = build_context()

    try:
        RemoteVerification(
            context=context,
            case=DiagnosticCase(),
        )
    except ValueError:
        return

    assert False


def test_creates_canonical_production_engine():
    verification = build_verification()

    assert type(verification.engine) is ProductionProblemSolvingEngine


def test_engine_uses_same_case():
    verification = build_verification()

    assert verification.engine.case is verification.case


def test_engine_uses_same_workflow():
    verification = build_verification()

    assert verification.engine.workflow is verification.workflow


def test_preserves_remote_identity():
    verification = build_verification()

    assert verification.machine_id == "machine-001"
    assert verification.hostname == "REMOTE-PC"
    assert verification.session_id == (
        verification.context.session_id
    )
    assert verification.is_remote is True


def test_verification_delegates_to_canonical_engine():
    verification = build_verification()

    sentinel = object()

    verification.engine.verify_remediation = (
        lambda result=None, expected=None, observed=None: sentinel
    )

    result = verification.verify(
        result="result",
        expected="RESOLVED",
        observed="RESOLVED",
    )

    assert result is sentinel


def test_verification_stores_result():
    verification = build_verification()

    class VerificationResult:
        pass

    result = VerificationResult()

    verification.engine.verify_remediation = (
        lambda result=None, expected=None, observed=None: result
    )

    returned = verification.verify(
        result=result,
        expected="RESOLVED",
        observed="RESOLVED",
    )

    assert returned is result
    assert verification.verification_result is not result


def test_verification_complete_delegates():
    verification = build_verification()

    assert (
        verification.verification_complete
        == verification.engine.verification_complete
    )


def test_no_remote_execute_method():
    verification = build_verification()

    assert not hasattr(
        verification,
        "execute_remediation",
    )


def test_no_remote_authorization_method():
    verification = build_verification()

    assert not hasattr(
        verification,
        "authorize_remediation",
    )


def test_no_remote_retry_method():
    verification = build_verification()

    assert not hasattr(
        verification,
        "retry",
    )


def test_no_second_verifier():
    verification = build_verification()

    assert not hasattr(
        verification,
        "verifier",
    )


def test_no_second_workflow():
    verification = build_verification()

    assert verification.engine.workflow is verification.workflow


def test_remote_context_remains_execution_context():
    verification = build_verification()

    assert verification.context.is_remote is True
    assert verification.is_remote is True
