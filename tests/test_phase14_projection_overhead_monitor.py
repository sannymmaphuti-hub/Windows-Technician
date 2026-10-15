import pytest

from engine.projection_overhead_monitor import ProjectionOverheadMonitor


def test_projection_measurement_returns_original_result():
    monitor = ProjectionOverheadMonitor()
    result = monitor.measure("fleet_projection", lambda: {"machines": 3})

    assert result == {"machines": 3}
    snapshot = monitor.projection()
    assert snapshot["measurement_count"] == 1
    assert snapshot["measurements"][0]["succeeded"] is True


def test_projection_failure_is_measured_and_exception_propagates():
    monitor = ProjectionOverheadMonitor()

    def fail():
        raise RuntimeError("projection failed")

    with pytest.raises(RuntimeError, match="projection failed"):
        monitor.measure("case_projection", fail)

    snapshot = monitor.projection()
    assert snapshot["measurement_count"] == 1
    assert snapshot["measurements"][0]["succeeded"] is False


def test_projection_history_is_bounded():
    monitor = ProjectionOverheadMonitor(history_capacity=2)

    for value in range(3):
        monitor.measure("fleet_projection", lambda value=value: value)

    snapshot = monitor.projection()
    assert snapshot["measurement_count"] == 2
    assert snapshot["evicted_count"] == 1


def test_projection_does_not_enable_caching_or_provider_mutation():
    monitor = ProjectionOverheadMonitor()
    snapshot = monitor.projection()

    assert snapshot["caching_enabled"] is False
    assert snapshot["provider_mutation_performed"] is False


def test_projection_snapshot_is_detached():
    monitor = ProjectionOverheadMonitor()
    monitor.measure("case_projection", lambda: {"case_id": "A"})

    snapshot = monitor.projection()
    snapshot["measurements"][0]["projection_name"] = "tampered"

    assert (
        monitor.projection()["measurements"][0]["projection_name"]
        == "case_projection"
    )


@pytest.mark.parametrize("name", ["", "   ", None])
def test_invalid_projection_name_is_rejected(name):
    monitor = ProjectionOverheadMonitor()

    with pytest.raises((TypeError, ValueError)):
        monitor.measure(name, lambda: None)


def test_non_callable_projection_is_rejected():
    monitor = ProjectionOverheadMonitor()

    with pytest.raises(TypeError):
        monitor.measure("case_projection", None)
