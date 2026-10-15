from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.reliability_service import ReliabilityService
from engine.operation_lifecycle_tracker import OperationLifecycleTracker
from engine.observability_boundary import ObservabilityBoundary
from engine.operation_metrics import OperationMetricsCollector
from engine.reliability_metrics import ReliabilityMetricsCollector
from engine.observability_event_history import ObservabilityEventHistory
from engine.technician_observability_projection import (
    TechnicianObservabilityProjection,
)


def make_components():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case,
        workflow,
        WindowsDiagnosticEngineRegistry(),
    )
    reliability = ReliabilityService(workflow)
    return case, workflow, engine, reliability


def test_real_reliability_projection_produces_actual_metrics():
    _, _, _, reliability = make_components()

    operation = reliability.create_operation("diagnostic")
    reliability.start_operation(operation.operation_id)
    reliability.complete_operation(operation.operation_id)

    metrics = ReliabilityMetricsCollector(reliability).projection()

    assert metrics["operation_status_counts"]["SUCCEEDED"] == 1
    assert metrics["failed_operation_count"] == 0
    assert metrics["retry_decision_count"] == 0
    assert metrics["recovery_record_count"] == 0


def test_real_operation_tracker_metrics_are_integrated():
    tracker = OperationLifecycleTracker()
    operation = tracker.create("diagnostic")

    metrics = OperationMetricsCollector(tracker).projection()

    assert metrics["total_operations"] == 1
    assert metrics["by_status"]["PENDING"] == 1

    tracker.transition(operation.operation_id, operation.status.RUNNING)

    updated = OperationMetricsCollector(tracker).projection()
    assert updated["by_status"]["RUNNING"] == 1


def test_real_engine_and_reliability_service_share_observability_boundary():
    case, workflow, engine, reliability = make_components()

    boundary = ObservabilityBoundary(
        engine,
        reliability,
        telemetry_enabled=False,
    )

    snapshot = boundary.projection()

    assert snapshot["telemetry_enabled"] is False
    assert isinstance(snapshot["engine"], dict)
    assert isinstance(snapshot["reliability"], dict)

    # Reading observability must not change workflow or engine state.
    workflow_state_before = workflow.state
    engine_state_before = engine.projection()["state"]

    boundary.projection()

    assert workflow.state == workflow_state_before
    assert engine.projection()["state"] == engine_state_before
    assert engine.case is case


def test_combined_projection_reads_real_subsystems_without_mutating_them():
    _, _, engine, reliability = make_components()
    tracker = OperationLifecycleTracker()
    tracker.create("diagnostic")

    boundary = ObservabilityBoundary(
        engine,
        reliability,
        telemetry_enabled=False,
    )
    history = ObservabilityEventHistory()

    combined = TechnicianObservabilityProjection(
        observability_boundary=boundary,
        operation_metrics=OperationMetricsCollector(tracker),
        reliability_metrics=ReliabilityMetricsCollector(reliability),
        event_history=history,
    )

    before = reliability.projection()
    first = combined.projection()
    second = combined.projection()
    after = reliability.projection()

    assert first["observability"]["telemetry_enabled"] is False
    assert first["operation_metrics"]["total_operations"] == 1
    assert first["reliability_metrics"]["operation_status_counts"]["PENDING"] == 0
    assert first["event_history"]["event_count"] == 0
    assert first["generated_at"] != "" and second["generated_at"] != ""
    assert before == after


def test_real_reliability_metrics_snapshots_are_independent():
    _, _, _, reliability = make_components()
    operation = reliability.create_operation("diagnostic")
    reliability.start_operation(operation.operation_id)
    reliability.complete_operation(operation.operation_id)

    collector = ReliabilityMetricsCollector(reliability)

    first = collector.projection()
    first["operation_status_counts"]["SUCCEEDED"] = 999

    second = collector.projection()

    assert second["operation_status_counts"]["SUCCEEDED"] == 1
