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
from engine.windows_diagnostic_result import WindowsDiagnosticResult
from engine.recommendation import Recommendation


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


def make_high_recommendation():
    return Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review excessive memory consumption.",
        rationale="Memory pressure exceeds the configured threshold.",
    )


def prepare_action_engine():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.set_result(
        make_result([make_high_recommendation()])
    )
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True

    engine.prepare_remediation_authorization()

    action_id = next(iter(engine.remediation_actions))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)

    return engine, action_id


# ============================================================
# 1. Initial lifecycle invariants
# ============================================================

def test_7_19_initial_engine_is_open():
    engine = make_engine()

    assert engine.state == ProblemSolvingState.PENDING
    assert engine.workflow.state == WorkflowState.OPEN


def test_7_19_initial_recovery_cycle_is_original():
    engine = make_engine()

    cycle = engine.current_recovery_cycle

    assert cycle.cycle_number == 0
    assert cycle.is_original is True
    assert cycle.is_recovery is False


# ============================================================
# 2. Investigation invariants
# ============================================================

def test_7_19_investigation_moves_workflow_only_through_canonical_transition():
    engine = make_engine()

    engine.workflow.start_investigation()

    assert engine.workflow.state == WorkflowState.INVESTIGATING
    assert engine.workflow.history[-1] == (
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
    )


# ============================================================
# 3. Diagnosis invariants
# ============================================================

def test_7_19_diagnosis_requires_investigation():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.workflow.mark_diagnosed()


def test_7_19_diagnosis_creates_canonical_result():
    engine = make_engine()

    engine.workflow.start_investigation()

    result = make_result()
    engine.set_result(result)
    engine.workflow.mark_diagnosed()

    assert isinstance(engine.result, WindowsDiagnosticResult)
    assert engine.workflow.state == WorkflowState.DIAGNOSED


# ============================================================
# 4. Decision invariants
# ============================================================

def test_7_19_no_eligible_recommendation_keeps_case_diagnosed():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.set_result(make_result())
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is False
    assert engine.workflow.state == WorkflowState.DIAGNOSED


def test_7_19_high_recommendation_requires_action():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.set_result(
        make_result([make_high_recommendation()])
    )
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True
    assert engine.workflow.state == WorkflowState.ACTION_REQUIRED


# ============================================================
# 5. Authorization invariants
# ============================================================

def test_7_19_prepared_action_is_not_executable():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.set_result(
        make_result([make_high_recommendation()])
    )
    engine.workflow.mark_diagnosed()
    engine.evaluate_action_requirement()
    engine.prepare_remediation_authorization()

    action_id = next(iter(engine.remediation_actions))

    assert engine.authorization_allows_execution(action_id) is False
    assert engine._execution_boundary_available() is False


def test_7_19_authorization_plus_operation_opens_execution_boundary():
    engine, action_id = prepare_action_engine()

    assert engine.authorization_allows_execution(action_id) is True
    assert engine._execution_boundary_available() is True


# ============================================================
# 6. Execution invariants
# ============================================================

def test_7_19_execution_moves_workflow_to_verifying():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    assert result.execution_status == "EXECUTED"
    assert engine.workflow.state == WorkflowState.VERIFYING


def test_7_19_executed_action_is_no_longer_available():
    engine, action_id = prepare_action_engine()

    engine.execute_remediation(action_id)

    assert engine._execution_boundary_available() is False


# ============================================================
# 7. Verification invariants
# ============================================================

def test_7_19_successful_verification_resolves_case():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    verified = engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert verified["verified"] is True
    assert engine.workflow.state == WorkflowState.RESOLVED
    assert engine.state == ProblemSolvingState.RESOLVED
    assert engine.verification_complete is True


def test_7_19_failed_verification_returns_to_remediation():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    verified = engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still unhealthy",
    )

    assert verified["verified"] is False
    assert engine.workflow.state == WorkflowState.REMEDIATING
    assert engine.state == ProblemSolvingState.ACTION_REQUIRED


# ============================================================
# 8. Recovery invariants
# ============================================================

def test_7_19_recovery_requires_explicit_start():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still unhealthy",
    )

    assert engine.recovery_cycle_count == 1

    cycle = engine.start_recovery_cycle()

    assert cycle.cycle_number == 1
    assert cycle.is_recovery is True
    assert engine.recovery_cycle_count == 2
    assert engine.workflow.state == WorkflowState.INVESTIGATING


def test_7_19_recovery_preserves_original_cycle():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still unhealthy",
    )

    engine.start_recovery_cycle()

    cycles = engine.recovery_cycles

    assert cycles[0].cycle_number == 0
    assert cycles[0].is_original is True
    assert cycles[1].cycle_number == 1
    assert cycles[1].is_recovery is True


# ============================================================
# 9. Terminal-state invariants
# ============================================================

def test_7_19_resolved_case_cannot_start_recovery():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert engine.workflow.state == WorkflowState.RESOLVED

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()


def test_7_19_resolved_case_cannot_execute_again():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    with pytest.raises(ValueError):
        engine.execute_remediation(action_id)


# ============================================================
# 10. Projection invariants
# ============================================================

def test_7_19_projection_matches_workflow_state():
    engine, action_id = prepare_action_engine()

    projection = engine.projection()

    assert projection["workflow_state"] == engine.workflow.state


def test_7_19_projection_history_is_canonical():
    engine, action_id = prepare_action_engine()

    engine.execute_remediation(action_id)

    projection = engine.projection()

    assert len(projection["lifecycle_history"]) == len(
        engine.workflow.history
    )

    for item, transition in zip(
        projection["lifecycle_history"],
        engine.workflow.history,
    ):
        assert item["from"] == transition[0].value
        assert item["to"] == transition[1].value


def test_7_19_projection_recovery_count_matches_history():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still unhealthy",
    )

    engine.start_recovery_cycle()

    projection = engine.projection()

    assert projection["recovery_cycle_count"] == 2
    assert len(projection["recovery_cycles"]) == 2
