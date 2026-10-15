from concurrent.futures import ThreadPoolExecutor

from engine.bounded_execution_coordinator import BoundedExecutionCoordinator
from engine.diagnostic_performance_profiler import DiagnosticPerformanceProfiler
from engine.fleet_workload_policy import FleetWorkloadPolicy
from engine.performance_scale_boundary import PerformanceLimits
from engine.projection_overhead_monitor import ProjectionOverheadMonitor


def test_profiler_retains_only_configured_number_of_samples():
    profiler = DiagnosticPerformanceProfiler(history_capacity=50)

    for value in range(500):
        profiler.record("diagnostic", value / 1000)

    result = profiler.projection()
    assert len(result["samples"]) == 50
    assert result["evicted_count"] == 450
    assert result["summary"]["sample_count"] == 50


def test_projection_monitor_retains_only_configured_measurements():
    monitor = ProjectionOverheadMonitor(history_capacity=40)

    for value in range(300):
        monitor.measure("dashboard", lambda value=value: value)

    result = monitor.projection()
    assert result["measurement_count"] == 40
    assert result["evicted_count"] == 260


def test_concurrent_reservations_never_exceed_capacity():
    capacity = 8
    coordinator = BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=capacity,
            max_managed_machines=500,
            max_events_retained=1000,
            max_projection_items=1000,
        )
    )

    def reserve():
        return coordinator.reserve()

    with ThreadPoolExecutor(max_workers=32) as executor:
        decisions = list(executor.map(lambda _: reserve(), range(100)))

    admitted = [item for item in decisions if item.admitted]
    rejected = [item for item in decisions if not item.admitted]

    assert len(admitted) == capacity
    assert len(rejected) == 100 - capacity
    assert len(coordinator.projection()["active_reservations"]) == capacity


def test_fleet_admission_is_repeatable_for_same_capacity_state():
    policy = FleetWorkloadPolicy()

    first = policy.evaluate(fleet_size=4).projection()
    second = policy.evaluate(fleet_size=4).projection()

    assert first == second


def test_performance_measurements_do_not_change_callback_results():
    profiler = DiagnosticPerformanceProfiler()
    monitor = ProjectionOverheadMonitor()

    def operation():
        return {"value": 42, "items": [1, 2, 3]}

    expected = operation()
    measured = profiler.measure("operation", operation)
    projected = monitor.measure("projection", operation)

    assert measured == expected
    assert projected == expected
