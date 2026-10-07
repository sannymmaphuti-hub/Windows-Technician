"""Tests for the production performance boundary."""

import time

import pytest

from packaging.performance_boundary import (
    PerformanceBudget,
    PerformanceMeasurement,
    STARTUP_PERFORMANCE_BUDGET,
    measure_operation,
    startup_performance_is_acceptable,
)


def test_measurement_stores_operation():
    measurement = PerformanceMeasurement(
        operation="startup",
        elapsed_seconds=0.25,
    )

    assert measurement.operation == "startup"


def test_measurement_stores_elapsed_time():
    measurement = PerformanceMeasurement(
        operation="startup",
        elapsed_seconds=0.25,
    )

    assert measurement.elapsed_seconds == 0.25


def test_measurement_converts_to_milliseconds():
    measurement = PerformanceMeasurement(
        operation="startup",
        elapsed_seconds=0.25,
    )

    assert measurement.elapsed_milliseconds == 250.0


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        PerformanceMeasurement(
            operation="",
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_time():
    with pytest.raises(ValueError):
        PerformanceMeasurement(
            operation="startup",
            elapsed_seconds=-0.1,
        )


def test_budget_stores_operation():
    budget = PerformanceBudget(
        operation="startup",
        maximum_seconds=1.0,
    )

    assert budget.operation == "startup"


def test_budget_requires_positive_limit():
    with pytest.raises(ValueError):
        PerformanceBudget(
            operation="startup",
            maximum_seconds=0,
        )


def test_budget_accepts_measurement_within_limit():
    budget = PerformanceBudget(
        operation="startup",
        maximum_seconds=1.0,
    )

    measurement = PerformanceMeasurement(
        operation="startup",
        elapsed_seconds=0.5,
    )

    assert budget.accepts(measurement)


def test_budget_rejects_measurement_over_limit():
    budget = PerformanceBudget(
        operation="startup",
        maximum_seconds=1.0,
    )

    measurement = PerformanceMeasurement(
        operation="startup",
        elapsed_seconds=1.1,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_wrong_operation():
    budget = PerformanceBudget(
        operation="startup",
        maximum_seconds=1.0,
    )

    measurement = PerformanceMeasurement(
        operation="dashboard",
        elapsed_seconds=0.1,
    )

    assert not budget.accepts(measurement)


def test_measure_operation_returns_callback_result():
    result, measurement = measure_operation(
        "test",
        lambda: 42,
    )

    assert result == 42
    assert measurement.operation == "test"


def test_measure_operation_records_elapsed_time():
    _, measurement = measure_operation(
        "test",
        lambda: time.sleep(0.01),
    )

    assert measurement.elapsed_seconds >= 0.01


def test_measure_operation_rejects_invalid_operation():
    with pytest.raises(ValueError):
        measure_operation(
            "",
            lambda: None,
        )


def test_measure_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_operation(
            "test",
            None,
        )


def test_measure_operation_preserves_callback_exception():
    def failing_operation():
        raise RuntimeError("expected failure")

    with pytest.raises(RuntimeError):
        measure_operation(
            "test",
            failing_operation,
        )


def test_startup_budget_targets_application_startup():
    assert (
        STARTUP_PERFORMANCE_BUDGET.operation
        == "application_startup"
    )


def test_startup_budget_is_five_seconds():
    assert (
        STARTUP_PERFORMANCE_BUDGET.maximum_seconds
        == 5.0
    )


def test_startup_measurement_within_budget():
    measurement = PerformanceMeasurement(
        operation="application_startup",
        elapsed_seconds=1.0,
    )

    assert startup_performance_is_acceptable(
        measurement
    )


def test_startup_measurement_over_budget():
    measurement = PerformanceMeasurement(
        operation="application_startup",
        elapsed_seconds=5.01,
    )

    assert not startup_performance_is_acceptable(
        measurement
    )
