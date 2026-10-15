import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.windows_diagnostic_engine_registry import WindowsDiagnosticEngineRegistry
from engine.windows_diagnostic_result import WindowsDiagnosticResult
from engine.problem_solving_engine import (
    ProductionProblemSolvingEngine,
    ProblemSolvingState,
)


def make_engine():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=registry,
    )


def make_result(recommendations=None):
    return WindowsDiagnosticResult(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        primary_cause=None,
        recommendations=recommendations or [],
        confidences=[],
    )


# ============================================================
# 1. Construction contract
# ============================================================

def test_7_18_constructor_rejects_invalid_case():
    workflow = TechnicianWorkflow(DiagnosticCase())
    registry = WindowsDiagnosticEngineRegistry()

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case=object(),
            workflow=workflow,
            diagnostic_registry=registry,
        )


def test_7_18_constructor_rejects_invalid_workflow():
    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case=DiagnosticCase(),
            workflow=object(),
            diagnostic_registry=WindowsDiagnosticEngineRegistry(),
        )


def test_7_18_constructor_rejects_invalid_registry():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case=case,
            workflow=workflow,
            diagnostic_registry=object(),
        )


def test_7_18_constructor_requires_workflow_case_identity():
    case = DiagnosticCase()
    different_case = DiagnosticCase()
    workflow = TechnicianWorkflow(different_case)

    with pytest.raises(ValueError, match="reference"):
        ProductionProblemSolvingEngine(
            case=case,
            workflow=workflow,
            diagnostic_registry=WindowsDiagnosticEngineRegistry(),
        )


# ============================================================
# 2. Result contract
# ============================================================

def test_7_18_set_result_accepts_canonical_result():
    engine = make_engine()
    result = make_result()

    returned = engine.set_result(result)

    assert isinstance(returned, WindowsDiagnosticResult)
    assert engine.result is not result


def test_7_18_set_result_rejects_none():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.set_result(None)


def test_7_18_result_property_is_defensive():
    engine = make_engine()
    engine.set_result(make_result())

    first = engine.result
    second = engine.result

    assert first is not second


# ============================================================
# 3. State contract
# ============================================================

def test_7_18_set_state_rejects_invalid_state():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.set_state("NOT_A_REAL_STATE")


def test_7_18_set_state_accepts_canonical_state():
    engine = make_engine()

    engine.set_state(ProblemSolvingState.PENDING)

    assert engine.state == ProblemSolvingState.PENDING


# ============================================================
# 4. Failure contract
# ============================================================

def test_7_18_fail_records_exception_metadata():
    engine = make_engine()

    result = engine.fail(RuntimeError("diagnostic failure"))

    assert result["type"] == "RuntimeError"
    assert result["message"] == "diagnostic failure"
    assert engine.state == ProblemSolvingState.FAILED


def test_7_18_failure_property_is_defensive():
    engine = make_engine()
    engine.fail(RuntimeError("failure"))

    first = engine.failure
    first["message"] = "mutated"

    assert engine.failure["message"] == "failure"


# ============================================================
# 5. Diagnostic execution contract
# ============================================================

def test_7_18_execute_domains_rejects_unknown_domain():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.execute_domains(["NOT_A_DOMAIN"])


def test_7_18_dispatch_domain_rejects_unknown_domain():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.dispatch_domain("NOT_A_DOMAIN")


def test_7_18_execute_domains_requires_domains():
    engine = make_engine()

    with pytest.raises((ValueError, TypeError)):
        engine.execute_domains(None)


# ============================================================
# 6. Aggregation contract
# ============================================================

def test_7_18_aggregate_requires_available_domain_result():
    engine = make_engine()

    engine._domain_results = {}

    with pytest.raises(ValueError):
        engine.aggregate_domain_results()


def test_7_18_aggregate_produces_canonical_result():
    engine = make_engine()

    engine._domain_results = {
        "MEMORY": make_result(),
    }

    result = engine.aggregate_domain_results()

    assert isinstance(result, WindowsDiagnosticResult)
    assert engine.result is not None


# ============================================================
# 7. Decision contract
# ============================================================

def test_7_18_decision_without_recommendations_is_safe():
    engine = make_engine()
    engine.set_result(make_result())

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is False
    assert engine.workflow.state == WorkflowState.DIAGNOSED


# ============================================================
# 8. Authorization contract
# ============================================================

def test_7_18_authorization_requires_existing_action():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.authorize_remediation("missing-action")


def test_7_18_denial_requires_existing_action():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.deny_remediation("missing-action")


def test_7_18_authorization_lookup_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises(ValueError, match="Unknown remediation action"):
        engine.authorization_for("missing-action")


# ============================================================
# 9. Execution contract
# ============================================================

def test_7_18_execution_rejects_unknown_action():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.execute_remediation("missing-action")


def test_7_18_execution_boundary_is_read_only():
    engine = make_engine()

    before = engine.workflow.state
    available = engine._execution_boundary_available()
    after = engine.workflow.state

    assert available is False
    assert before == after


# ============================================================
# 10. Verification contract
# ============================================================

def test_7_18_verification_is_incomplete_before_execution():
    engine = make_engine()

    assert engine.verification_complete is False
    assert engine.verification_result is None


# ============================================================
# 11. Recovery contract
# ============================================================

def test_7_18_recovery_requires_remediating_workflow():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()


def test_7_18_initial_recovery_history_is_present():
    engine = make_engine()

    assert engine.recovery_cycle_count == 1
    assert engine.current_recovery_cycle.is_original is True
    assert engine.current_recovery_cycle.cycle_number == 0


# ============================================================
# 12. Projection contract
# ============================================================

def test_7_18_projection_is_dictionary():
    engine = make_engine()

    projection = engine.projection()

    assert isinstance(projection, dict)


def test_7_18_projection_contains_core_contract():
    engine = make_engine()

    projection = engine.projection()

    required = {
        "case_id",
        "machine_id",
        "state",
        "workflow_state",
        "lifecycle_history",
        "result",
        "failure",
        "domain_results",
        "domain_failures",
        "remediation_actions",
        "authorizations",
        "execution_available",
        "verification_result",
        "verification_complete",
        "recovery_cycle_count",
        "recovery_cycles",
        "current_recovery_cycle",
    }

    assert required.issubset(projection.keys())


def test_7_18_projection_does_not_mutate_workflow():
    engine = make_engine()

    before = engine.workflow.state
    engine.projection()
    after = engine.workflow.state

    assert before == after


def test_7_18_projection_lifecycle_history_matches_workflow():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    projection = engine.projection()

    assert len(projection["lifecycle_history"]) == len(
        engine.workflow.history
    )
