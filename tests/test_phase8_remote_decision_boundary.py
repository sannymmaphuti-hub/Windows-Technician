from engine.diagnostic_case import DiagnosticCase
from engine.remote_decision_boundary import RemoteDecisionBoundary
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

    return RemoteDecisionBoundary(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )


def test_requires_diagnostic_case():
    try:
        RemoteDecisionBoundary("not-a-case")
    except ValueError:
        return

    assert False


def test_requires_remote_case():
    case = DiagnosticCase()

    try:
        RemoteDecisionBoundary(case)
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


def test_uses_canonical_registry():
    boundary = build_boundary()

    assert isinstance(
        boundary.diagnostic_registry,
        WindowsDiagnosticEngineRegistry,
    )


def test_preserves_remote_case_identity():
    boundary = build_boundary()

    assert boundary.case.machine_id == "machine-001"
    assert boundary.case.hostname == "REMOTE-PC"
    assert boundary.case.session_id == "session-001"
    assert boundary.case.origin == "REMOTE"


def test_decision_is_not_available_before_evaluation():
    boundary = build_boundary()

    assert boundary.decision is None
    assert boundary.eligible is None
    assert boundary.recommendation_type is None


def test_evaluation_delegates_to_production_engine():
    boundary = build_boundary()

    expected = object()

    def fake_evaluate():
        return expected

    boundary.engine.evaluate_action_requirement = fake_evaluate

    result = boundary.evaluate()

    assert result is not expected
    assert boundary.decision is not expected


def test_decision_is_stored():
    boundary = build_boundary()

    class Decision:
        eligible = True
        recommendation_type = "TEST"

    boundary.engine.evaluate_action_requirement = (
        lambda: Decision()
    )

    result = boundary.evaluate()

    assert result.eligible is True
    assert result.recommendation_type == "TEST"
    assert boundary.eligible is True
    assert boundary.recommendation_type == "TEST"


def test_evaluation_does_not_authorize():
    boundary = build_boundary()

    class Decision:
        eligible = True
        recommendation_type = "TEST"

    boundary.engine.evaluate_action_requirement = (
        lambda: Decision()
    )

    boundary.evaluate()

    assert not hasattr(boundary, "authorize_remediation")


def test_evaluation_does_not_execute():
    boundary = build_boundary()

    class Decision:
        eligible = True
        recommendation_type = "TEST"

    boundary.engine.evaluate_action_requirement = (
        lambda: Decision()
    )

    boundary.evaluate()

    assert not hasattr(boundary, "execute_remediation")


def test_remote_boundary_has_single_case():
    boundary = build_boundary()

    assert boundary.engine.case is boundary.case
    assert boundary.workflow.case is boundary.case


def test_remote_boundary_has_single_workflow():
    boundary = build_boundary()

    assert boundary.engine.workflow is boundary.workflow
