from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
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


def test_7_16_projection_exposes_schema_version():
    engine = make_engine()

    projection = engine.projection()

    assert projection["projection_schema_version"] == "1.0"


def test_7_16_schema_version_is_stable_across_projections():
    engine = make_engine()

    first = engine.projection()
    second = engine.projection()

    assert first["projection_schema_version"] == "1.0"
    assert second["projection_schema_version"] == "1.0"


def test_7_16_projection_has_stable_top_level_contract():
    engine = make_engine()

    projection = engine.projection()

    required_keys = {
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
        "verification_result",
        "verification_complete",
        "recovery_cycle_count",
        "recovery_cycles",
        "current_recovery_cycle",
    }

    assert required_keys.issubset(projection.keys())


def test_7_16_projection_schema_version_is_not_derived_from_runtime_state():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    projection = engine.projection()

    assert projection["projection_schema_version"] == "1.0"
    assert projection["workflow_state"] is WorkflowState.DIAGNOSED


def test_7_16_projection_preserves_current_workflow_state():
    engine = make_engine()

    engine.workflow.start_investigation()

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.INVESTIGATING


def test_7_16_projection_preserves_canonical_lifecycle_history():
    engine = make_engine()

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


def test_7_16_projection_is_safe_for_consumer_mutation():
    engine = make_engine()

    engine.workflow.start_investigation()

    projection = engine.projection()

    projection["lifecycle_history"].clear()

    fresh_projection = engine.projection()

    assert len(fresh_projection["lifecycle_history"]) == 1


def test_7_16_projection_nested_history_is_safe_for_consumer_mutation():
    engine = make_engine()

    engine.workflow.start_investigation()

    projection = engine.projection()

    projection["lifecycle_history"][0]["from"] = "CORRUPTED"

    fresh_projection = engine.projection()

    assert fresh_projection["lifecycle_history"][0]["from"] == (
        WorkflowState.OPEN.value
    )


def test_7_16_projection_does_not_mutate_workflow():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    state_before = engine.workflow.state
    history_before = list(engine.workflow.history)

    engine.projection()

    assert engine.workflow.state is state_before
    assert engine.workflow.history == history_before


def test_7_16_projection_remains_available_after_lifecycle_progression():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    projection = engine.projection()

    assert projection["projection_schema_version"] == "1.0"
    assert projection["workflow_state"] is WorkflowState.REMEDIATING
    assert len(projection["lifecycle_history"]) == 4


def test_7_16_projection_contract_contains_recovery_surface():
    engine = make_engine()

    projection = engine.projection()

    assert projection["recovery_cycle_count"] == 1
    assert len(projection["recovery_cycles"]) == 1
    assert projection["current_recovery_cycle"]["cycle_number"] == 0


def test_7_16_projection_contract_contains_remediation_surface():
    engine = make_engine()

    projection = engine.projection()

    assert "remediation_actions" in projection
    assert "authorizations" in projection
    assert "execution_available" in projection


def test_7_16_projection_contract_contains_verification_surface():
    engine = make_engine()

    projection = engine.projection()

    assert projection["verification_result"] is None
    assert projection["verification_complete"] is False


def test_7_16_projection_contract_is_additive_only():
    engine = make_engine()

    projection = engine.projection()

    assert projection["projection_schema_version"] == "1.0"
    assert projection["case_id"] == engine.case.case_id
    assert projection["workflow_state"] is engine.workflow.state
