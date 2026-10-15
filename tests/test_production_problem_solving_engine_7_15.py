import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.windows_diagnostic_engine_registry import WindowsDiagnosticEngineRegistry


def make_engine(dispatcher=None, coordinator=None):
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return ProductionProblemSolvingEngine(
        case,
        workflow,
        registry,
        dispatcher=dispatcher,
        coordinator=coordinator,
    )


def _make_7_15_engine():
    return make_engine()


def test_7_15_projection_exposes_lifecycle_history():
    engine = _make_7_15_engine()

    projection = engine.projection()

    assert "lifecycle_history" in projection
    assert projection["lifecycle_history"] == []


def test_7_15_history_reflects_workflow_transitions():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    projection = engine.projection()

    assert projection["lifecycle_history"] == [
        {
            "from": WorkflowState.OPEN.value,
            "to": WorkflowState.INVESTIGATING.value,
        },
        {
            "from": WorkflowState.INVESTIGATING.value,
            "to": WorkflowState.DIAGNOSED.value,
        },
    ]


def test_7_15_history_preserves_transition_order():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()
    engine.workflow.start_verification()
    engine.workflow.resolve()

    history = engine.projection()["lifecycle_history"]

    assert [entry["from"] for entry in history] == [
        WorkflowState.OPEN.value,
        WorkflowState.INVESTIGATING.value,
        WorkflowState.DIAGNOSED.value,
        WorkflowState.ACTION_REQUIRED.value,
        WorkflowState.REMEDIATING.value,
        WorkflowState.VERIFYING.value,
    ]

    assert [entry["to"] for entry in history] == [
        WorkflowState.INVESTIGATING.value,
        WorkflowState.DIAGNOSED.value,
        WorkflowState.ACTION_REQUIRED.value,
        WorkflowState.REMEDIATING.value,
        WorkflowState.VERIFYING.value,
        WorkflowState.RESOLVED.value,
    ]


def test_7_15_history_reflects_resolution():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()
    engine.workflow.start_verification()
    engine.workflow.resolve()

    history = engine.projection()["lifecycle_history"]

    assert history[-1] == {
        "from": WorkflowState.VERIFYING.value,
        "to": WorkflowState.RESOLVED.value,
    }


def test_7_15_history_reflects_recovery_investigation():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    engine.workflow.start_recovery_investigation()

    history = engine.projection()["lifecycle_history"]

    assert history[-1] == {
        "from": WorkflowState.REMEDIATING.value,
        "to": WorkflowState.INVESTIGATING.value,
    }


def test_7_15_history_reflects_explicit_recovery_cycle():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    engine.start_recovery_cycle()

    history = engine.projection()["lifecycle_history"]

    assert history[-1] == {
        "from": WorkflowState.REMEDIATING.value,
        "to": WorkflowState.INVESTIGATING.value,
    }


def test_7_15_history_projection_is_defensive():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()

    projection = engine.projection()
    projection["lifecycle_history"].clear()

    fresh_projection = engine.projection()

    assert len(fresh_projection["lifecycle_history"]) == 1


def test_7_15_history_entries_are_read_only_projection_data():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()

    projection = engine.projection()
    projection["lifecycle_history"][0]["from"] = "CORRUPTED"

    fresh_projection = engine.projection()

    assert fresh_projection["lifecycle_history"][0]["from"] == (
        WorkflowState.OPEN.value
    )


def test_7_15_projection_contains_current_and_historical_state():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.DIAGNOSED
    assert projection["lifecycle_history"][-1] == {
        "from": WorkflowState.INVESTIGATING.value,
        "to": WorkflowState.DIAGNOSED.value,
    }


def test_7_15_history_does_not_create_parallel_workflow_state():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()

    projection = engine.projection()

    expected = [
        {
            "from": previous.value,
            "to": current.value,
        }
        for previous, current in engine.workflow.history
    ]

    assert projection["lifecycle_history"] == expected


def test_7_15_projection_is_side_effect_free():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    before_state = engine.workflow.state
    before_history = list(engine.workflow.history)

    engine.projection()

    assert engine.workflow.state is before_state
    assert engine.workflow.history == before_history


def test_7_15_recovery_preserves_previous_lifecycle_history():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    before_recovery = engine.projection()["lifecycle_history"]

    engine.start_recovery_cycle()

    after_recovery = engine.projection()["lifecycle_history"]

    assert after_recovery[:-1] == before_recovery
    assert after_recovery[-1] == {
        "from": WorkflowState.REMEDIATING.value,
        "to": WorkflowState.INVESTIGATING.value,
    }


def test_7_15_lifecycle_and_recovery_history_are_distinct_canonical_surfaces():
    engine = _make_7_15_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    engine.start_recovery_cycle()

    projection = engine.projection()

    assert projection["recovery_cycle_count"] == 2
    assert len(projection["lifecycle_history"]) == 5
    assert projection["current_recovery_cycle"]["cycle_number"] == 1
