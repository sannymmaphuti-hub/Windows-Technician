from concurrent.futures import ThreadPoolExecutor

from engine.bounded_execution_coordinator import BoundedExecutionCoordinator
from engine.diagnostic_performance_profiler import DiagnosticPerformanceProfiler
from engine.fleet_workload_policy import FleetWorkloadPolicy
from engine.performance_scale_boundary import PerformanceLimits
from engine.projection_overhead_monitor import ProjectionOverheadMonitor


def test_integrated_fleet_admission_and_execution_capacity():
    capacity = 8

    coordinator = BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=capacity,
            max_managed_machines=500,
            max_events_retained=1000,
            max_projection_items=1000,
        ),
        history_capacity=20,
    )
    fleet_policy = FleetWorkloadPolicy()

    admission = fleet_policy.evaluate(fleet_size=4)
    assert admission.admitted

    def attempt_reservation(_):
        return coordinator.reserve()

    with ThreadPoolExecutor(max_workers=32) as executor:
        decisions = list(executor.map(attempt_reservation, range(100)))

    admitted = [decision for decision in decisions if decision.admitted]
    rejected = [decision for decision in decisions if not decision.admitted]

    assert len(admitted) == capacity
    assert len(rejected) == 100 - capacity

    snapshot = coordinator.projection()
    assert len(snapshot["active_reservations"]) == capacity
    assert snapshot["execution_performed"] is False

    for decision in admitted:
        assert coordinator.complete(decision.reservation_id)

    final_snapshot = coordinator.projection()
    assert final_snapshot["active_reservations"] == []
    assert len(final_snapshot["history"]) <= 20


def test_profiler_and_projection_monitor_survive_concurrent_measurements():
    profiler = DiagnosticPerformanceProfiler(history_capacity=25)
    monitor = ProjectionOverheadMonitor(history_capacity=25)

    def collect(index):
        profiler.record("diagnostic", index / 1000)
        return monitor.measure(
            "dashboard_projection",
            lambda: {"index": index},
        )

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(collect, range(200)))

    assert len(results) == 200
    assert all(isinstance(result, dict) for result in results)

    profiler_snapshot = profiler.projection()
    monitor_snapshot = monitor.projection()

    assert profiler_snapshot["summary"]["sample_count"] == 25
    assert profiler_snapshot["evicted_count"] == 175

    assert monitor_snapshot["measurement_count"] == 25
    assert monitor_snapshot["evicted_count"] == 175


def test_repeated_projection_does_not_change_active_reservations():
    coordinator = BoundedExecutionCoordinator()

    reservation = coordinator.reserve()
    assert reservation.admitted

    before = coordinator.projection()

    for _ in range(100):
        coordinator.projection()

    after = coordinator.projection()

    assert before["active_reservations"] == after["active_reservations"]
    assert len(after["active_reservations"]) == 1

    assert coordinator.release(reservation.reservation_id)


def test_capacity_remains_available_after_completed_work():
    coordinator = BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=2,
            max_managed_machines=10,
            max_events_retained=100,
            max_projection_items=100,
        )
    )

    first = coordinator.reserve()
    second = coordinator.reserve()

    assert first.admitted
    assert second.admitted
    assert not coordinator.reserve().admitted

    assert coordinator.complete(first.reservation_id)

    replacement = coordinator.reserve()
    assert replacement.admitted

    assert coordinator.release(second.reservation_id)
    assert coordinator.release(replacement.reservation_id)
