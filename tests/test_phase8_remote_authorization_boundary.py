from engine.diagnostic_case import DiagnosticCase
from engine.remote_authorization_boundary import (
    RemoteAuthorizationBoundary,
)
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


def build_case():
    case = DiagnosticCase()
    case.origin = "REMOTE"
    case.machine_id = "machine-001"
    case.hostname = "REMOTE-PC"
    case.session_id = "session-001"

    return case


def build_boundary():
    case = build_case()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return RemoteAuthorizationBoundary(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )


def test_requires_diagnostic_case():
    try:
        RemoteAuthorizationBoundary("not-a-case")
    except ValueError:
        return

    assert False


def test_requires_remote_origin():
    case = DiagnosticCase()

    try:
        RemoteAuthorizationBoundary(case)
    except ValueError:
        return

    assert False


def test_creates_canonical_workflow():
    boundary = build_boundary()

    assert type(boundary.workflow) is TechnicianWorkflow
    assert boundary.workflow.case is boundary.case


def test_uses_canonical_production_engine():
    boundary = build_boundary()

    assert boundary.engine.__class__.__name__ == (
        "ProductionProblemSolvingEngine"
    )


def test_preserves_remote_identity():
    boundary = build_boundary()

    assert boundary.case.machine_id == "machine-001"
    assert boundary.case.hostname == "REMOTE-PC"
    assert boundary.case.session_id == "session-001"
    assert boundary.case.origin == "REMOTE"


def test_prepare_delegates_to_canonical_engine():
    boundary = build_boundary()

    sentinel = object()

    boundary.engine.prepare_remediation_authorization = (
        lambda: sentinel
    )

    assert boundary.prepare() is sentinel


def test_authorize_delegates_to_canonical_engine():
    boundary = build_boundary()

    sentinel = object()

    boundary.engine.authorize_remediation = (
        lambda action_id, technician=False: sentinel
    )

    result = boundary.authorize(
        "action-001",
        technician=True,
    )

    assert result is sentinel


def test_deny_delegates_to_canonical_engine():
    boundary = build_boundary()

    sentinel = object()

    boundary.engine.deny_remediation = (
        lambda action_id, technician=False: sentinel
    )

    result = boundary.deny(
        "action-001",
        technician=True,
    )

    assert result is sentinel


def test_authorization_lookup_delegates():
    boundary = build_boundary()

    sentinel = object()

    boundary.engine.authorization_for = (
        lambda action_id: sentinel
    )

    assert boundary.authorization_for("action-001") is sentinel


def test_execution_gate_delegates():
    boundary = build_boundary()

    boundary.engine.authorization_allows_execution = (
        lambda action_id: True
    )

    assert boundary.authorization_allows_execution(
        "action-001"
    ) is True


def test_no_remote_execute_method():
    boundary = build_boundary()

    assert not hasattr(
        boundary,
        "execute_remediation",
    )


def test_no_remote_operation_binding():
    boundary = build_boundary()

    assert not hasattr(
        boundary,
        "bind_operation",
    )


def test_no_remote_verification():
    boundary = build_boundary()

    assert not hasattr(
        boundary,
        "verify_remediation",
    )


def test_authorization_does_not_execute():
    boundary = build_boundary()

    called = []

    def authorize(action_id, technician=False):
        called.append(
            (action_id, technician)
        )
        return "AUTHORIZED"

    boundary.engine.authorize_remediation = authorize

    result = boundary.authorize(
        "action-001",
        technician=True,
    )

    assert result == "AUTHORIZED"
    assert called == [
        ("action-001", True)
    ]
