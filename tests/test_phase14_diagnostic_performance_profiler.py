import pytest

from engine.diagnostic_performance_profiler import (
    DiagnosticPerformanceProfiler,
    PerformanceSample,
)


def test_measure_returns_callback_result_and_records_duration():
    profiler = DiagnosticPerformanceProfiler()
    result = profiler.measure("cpu_scan", lambda: "complete")

    snapshot = profiler.projection()
    assert result == "complete"
    assert snapshot["summary"]["sample_count"] == 1
    assert snapshot["samples"][0]["operation"] == "cpu_scan"
    assert snapshot["samples"][0]["duration_seconds"] >= 0


def test_measure_records_duration_when_callback_raises():
    profiler = DiagnosticPerformanceProfiler()

    def fail():
        raise RuntimeError("diagnostic failed")

    with pytest.raises(RuntimeError, match="diagnostic failed"):
        profiler.measure("memory_scan", fail)

    snapshot = profiler.projection()
    assert snapshot["summary"]["sample_count"] == 1
    assert snapshot["samples"][0]["operation"] == "memory_scan"


def test_record_produces_minimum_median_and_maximum():
    profiler = DiagnosticPerformanceProfiler()
    profiler.record("scan", 0.2)
    profiler.record("scan", 0.4)
    profiler.record("scan", 0.6)

    summary = profiler.projection()["summary"]
    assert summary == {
        "sample_count": 3,
        "minimum_seconds": 0.2,
        "median_seconds": 0.4,
        "maximum_seconds": 0.6,
    }


def test_history_is_bounded_and_evictions_are_counted():
    profiler = DiagnosticPerformanceProfiler(history_capacity=2)
    profiler.record("scan", 0.1)
    profiler.record("scan", 0.2)
    profiler.record("scan", 0.3)

    snapshot = profiler.projection()
    assert len(snapshot["samples"]) == 2
    assert snapshot["evicted_count"] == 1
    assert snapshot["samples"][0]["duration_seconds"] == 0.2


def test_projection_is_detached():
    profiler = DiagnosticPerformanceProfiler()
    profiler.record("scan", 0.1)

    snapshot = profiler.projection()
    snapshot["samples"][0]["operation"] = "tampered"
    snapshot["summary"]["sample_count"] = 999

    fresh = profiler.projection()
    assert fresh["samples"][0]["operation"] == "scan"
    assert fresh["summary"]["sample_count"] == 1


@pytest.mark.parametrize("operation", ["", "   ", None])
def test_invalid_operation_is_rejected(operation):
    profiler = DiagnosticPerformanceProfiler()

    with pytest.raises((TypeError, ValueError)):
        profiler.record(operation, 0.1)


@pytest.mark.parametrize("duration", [-1, float("inf"), float("nan"), True])
def test_invalid_duration_is_rejected(duration):
    with pytest.raises(ValueError):
        PerformanceSample("scan", duration)


@pytest.mark.parametrize("capacity", [0, -1])
def test_non_positive_capacity_is_rejected(capacity):
    with pytest.raises(ValueError):
        DiagnosticPerformanceProfiler(history_capacity=capacity)


def test_boolean_capacity_is_rejected():
    with pytest.raises(TypeError):
        DiagnosticPerformanceProfiler(history_capacity=True)


def test_non_callable_callback_is_rejected():
    profiler = DiagnosticPerformanceProfiler()

    with pytest.raises(TypeError):
        profiler.measure("scan", None)
