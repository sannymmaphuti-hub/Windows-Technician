import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import (
    ProductionProblemSolvingEngine,
    ProblemSolvingState,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


def make_engine():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return ProductionProblemSolvingEngine(
        case,
        workflow,
        registry,
    )


def test_7_17_invalid_domain_is_rejected():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.dispatch_domain("NOT_A_REAL_DOMAIN")

    assert engine.workflow.state is WorkflowState.OPEN


def test_7_17_invalid_domain_does_not_corrupt_results():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.dispatch_domain("NOT_A_REAL_DOMAIN")

    assert engine.domain_results == {}
    assert engine.domain_failures == {}


def test_7_17_execute_domains_rejects_non_iterable_domains():
    engine = make_engine()

    with pytest.raises((TypeError, ValueError)):
        engine.execute_domains(None)

    assert engine.workflow.state is WorkflowState.OPEN


def test_7_17_execute_domains_rejects_unknown_domain():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.execute_domains(["NOT_A_REAL_DOMAIN"])

    assert engine.workflow.state is WorkflowState.OPEN
    assert engine.domain_results == {}
    assert engine.domain_failures == {}


def test_7_17_set_result_rejects_invalid_result():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.set_result(object())

    assert engine.result is None


def test_7_17_set_state_rejects_invalid_state():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.set_state("NOT_A_PROBLEM_SOLVING_STATE")

    assert engine.state is ProblemSolvingState.PENDING


def test_7_17_fail_requires_error():
    engine = make_engine()

    with pytest.raises((ValueError, TypeError)):
        engine.fail(None)

    assert engine.failure is None


def test_7_17_authorization_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.authorize_remediation("unknown-action")

    assert engine.authorizations == {}


def test_7_17_denial_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.deny_remediation("unknown-action")

    assert engine.authorizations == {}


def test_7_17_authorization_query_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.authorization_for("unknown-action")


def test_7_17_execution_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.execute_remediation("unknown-action")

    assert engine.workflow.state is WorkflowState.OPEN


def test_7_17_verification_rejects_missing_result():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=None,
            expected="healthy",
            observed="healthy",
        )

    assert engine.verification_complete is False
    assert engine.workflow.state is WorkflowState.OPEN


def test_7_17_recovery_rejects_invalid_workflow_state():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()

    assert engine.workflow.state is WorkflowState.OPEN
    assert engine.recovery_cycle_count == 1


def test_7_17_invalid_operations_do_not_create_lifecycle_history():
    engine = make_engine()

    with pytest.raises((ValueError, KeyError)):
        engine.execute_remediation("unknown-action")

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=None,
            expected="healthy",
            observed="healthy",
        )

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()

    projection = engine.projection()

    assert projection["lifecycle_history"] == []
    assert projection["workflow_state"] is WorkflowState.OPEN


def test_7_17_invalid_operations_do_not_change_projection_contract():
    engine = make_engine()

    before = engine.projection()

    with pytest.raises((ValueError, KeyError)):
        engine.execute_remediation("unknown-action")

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()

    after = engine.projection()

    assert after["projection_schema_version"] == (
        before["projection_schema_version"]
    )
    assert after["case_id"] == before["case_id"]
    assert after["workflow_state"] is WorkflowState.OPEN
    assert after["lifecycle_history"] == []
    assert after["recovery_cycle_count"] == 1


def test_7_17_constructor_validation_remains_canonical():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            object(),
            workflow,
            registry,
        )

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case,
            object(),
            registry,
        )

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case,
            workflow,
            object(),
        )
