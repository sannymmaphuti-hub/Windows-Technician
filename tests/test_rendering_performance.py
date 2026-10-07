"""Tests for dashboard/rendering performance boundaries."""

import time

import pytest

from packaging.rendering_performance import (
    DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    RenderingPerformanceBudget,
    RenderingPerformanceMeasurement,
    dashboard_rendering_is_acceptable,
    large_dashboard_rendering_is_acceptable,
    measure_rendering_operation,
)


def test_rendering_budget_requires_operation():
    with pytest.raises(ValueError):
        RenderingPerformanceBudget(
            operation="",
            maximum_seconds=1.0,
        )


def test_rendering_budget_requires_positive_limit():
    with pytest.raises(ValueError):
        RenderingPerformanceBudget(
            operation="dashboard",
            maximum_seconds=0,
        )


def test_rendering_budget_accepts_value_within_limit():
    budget = RenderingPerformanceBudget(
        operation="dashboard",
        maximum_seconds=1.0,
    )

    assert budget.accepts(0.5)


def test_rendering_budget_rejects_value_over_limit():
    budget = RenderingPerformanceBudget(
        operation="dashboard",
        maximum_seconds=1.0,
    )

    assert not budget.accepts(1.01)


def test_rendering_budget_rejects_non_numeric_value():
    budget = RenderingPerformanceBudget(
        operation="dashboard",
        maximum_seconds=1.0,
    )

    with pytest.raises(TypeError):
        budget.accepts("1.0")


def test_rendering_budget_rejects_negative_value():
    budget = RenderingPerformanceBudget(
        operation="dashboard",
        maximum_seconds=1.0,
    )

    with pytest.raises(ValueError):
        budget.accepts(-0.1)


def test_measurement_stores_operation():
    measurement = RenderingPerformanceMeasurement(
        operation="dashboard",
        item_count=10,
        elapsed_seconds=0.5,
    )

    assert measurement.operation == "dashboard"


def test_measurement_stores_item_count():
    measurement = RenderingPerformanceMeasurement(
        operation="dashboard",
        item_count=10,
        elapsed_seconds=0.5,
    )

    assert measurement.item_count == 10


def test_measurement_converts_to_milliseconds():
    measurement = RenderingPerformanceMeasurement(
        operation="dashboard",
        item_count=10,
        elapsed_seconds=0.5,
    )

    assert measurement.elapsed_milliseconds == 500.0


def test_measurement_calculates_items_per_second():
    measurement = RenderingPerformanceMeasurement(
        operation="dashboard",
        item_count=100,
        elapsed_seconds=0.5,
    )

    assert measurement.items_per_second == 200.0


def test_zero_elapsed_time_reports_infinite_throughput():
    measurement = RenderingPerformanceMeasurement(
        operation="dashboard",
        item_count=100,
        elapsed_seconds=0.0,
    )

    assert measurement.items_per_second == float("inf")


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        RenderingPerformanceMeasurement(
            operation="",
            item_count=10,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_non_integer_item_count():
    with pytest.raises(TypeError):
        RenderingPerformanceMeasurement(
            operation="dashboard",
            item_count=10.5,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_item_count():
    with pytest.raises(ValueError):
        RenderingPerformanceMeasurement(
            operation="dashboard",
            item_count=-1,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_elapsed_time():
    with pytest.raises(ValueError):
        RenderingPerformanceMeasurement(
            operation="dashboard",
            item_count=10,
            elapsed_seconds=-0.1,
        )


def test_measure_rendering_operation_returns_result():
    result, measurement = measure_rendering_operation(
        "dashboard",
        100,
        lambda: ["finding"] * 100,
    )

    assert len(result) == 100
    assert measurement.operation == "dashboard"


def test_measure_rendering_operation_records_item_count():
    _, measurement = measure_rendering_operation(
        "dashboard",
        100,
        lambda: None,
    )

    assert measurement.item_count == 100


def test_measure_rendering_operation_records_elapsed_time():
    _, measurement = measure_rendering_operation(
        "dashboard",
        1,
        lambda: time.sleep(0.01),
    )

    assert measurement.elapsed_seconds >= 0.01


def test_measure_rendering_operation_rejects_invalid_operation():
    with pytest.raises(ValueError):
        measure_rendering_operation(
            "",
            10,
            lambda: None,
        )


def test_measure_rendering_operation_rejects_invalid_item_count():
    with pytest.raises(TypeError):
        measure_rendering_operation(
            "dashboard",
            10.5,
            lambda: None,
        )


def test_measure_rendering_operation_rejects_negative_item_count():
    with pytest.raises(ValueError):
        measure_rendering_operation(
            "dashboard",
            -1,
            lambda: None,
        )


def test_measure_rendering_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_rendering_operation(
            "dashboard",
            10,
            None,
        )


def test_dashboard_budget_is_one_second():
    assert (
        DASHBOARD_RENDERING_PERFORMANCE_BUDGET.maximum_seconds
        == 1.0
    )


def test_large_dashboard_budget_is_two_seconds():
    assert (
        LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET.maximum_seconds
        == 2.0
    )


def test_dashboard_rendering_accepts_fast_operation():
    assert dashboard_rendering_is_acceptable(0.5)


def test_dashboard_rendering_rejects_slow_operation():
    assert not dashboard_rendering_is_acceptable(1.01)


def test_large_dashboard_rendering_accepts_fast_operation():
    assert large_dashboard_rendering_is_acceptable(1.5)


def test_large_dashboard_rendering_rejects_slow_operation():
    assert not large_dashboard_rendering_is_acceptable(2.01)
