"""Tests for memory and resource pressure boundaries."""

import pytest

from packaging.resource_performance import (
    ResourceMeasurement,
    ResourcePerformanceBudget,
    SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET,
    current_process_memory_bytes,
    measure_resource_operation,
    resource_usage_is_acceptable,
)


def test_measurement_stores_operation():
    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.1,
        memory_before_bytes=1000,
        memory_after_bytes=2000,
    )

    assert measurement.operation == "intelligence"


def test_measurement_stores_memory_values():
    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.1,
        memory_before_bytes=1000,
        memory_after_bytes=2000,
    )

    assert measurement.memory_before_bytes == 1000
    assert measurement.memory_after_bytes == 2000


def test_measurement_calculates_memory_growth():
    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.1,
        memory_before_bytes=1000,
        memory_after_bytes=3000,
    )

    assert measurement.memory_growth_bytes == 2000


def test_measurement_calculates_negative_memory_growth():
    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.1,
        memory_before_bytes=3000,
        memory_after_bytes=1000,
    )

    assert measurement.memory_growth_bytes == -2000


def test_measurement_converts_memory_growth_to_megabytes():
    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.1,
        memory_before_bytes=0,
        memory_after_bytes=2 * 1024 * 1024,
    )

    assert measurement.memory_growth_megabytes == 2.0


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        ResourceMeasurement(
            operation="",
            elapsed_seconds=0.1,
            memory_before_bytes=0,
            memory_after_bytes=0,
        )


def test_measurement_rejects_negative_elapsed_time():
    with pytest.raises(ValueError):
        ResourceMeasurement(
            operation="intelligence",
            elapsed_seconds=-0.1,
            memory_before_bytes=0,
            memory_after_bytes=0,
        )


def test_measurement_rejects_non_integer_memory_before():
    with pytest.raises(TypeError):
        ResourceMeasurement(
            operation="intelligence",
            elapsed_seconds=0.1,
            memory_before_bytes=1.5,
            memory_after_bytes=0,
        )


def test_measurement_rejects_non_integer_memory_after():
    with pytest.raises(TypeError):
        ResourceMeasurement(
            operation="intelligence",
            elapsed_seconds=0.1,
            memory_before_bytes=0,
            memory_after_bytes=1.5,
        )


def test_measurement_rejects_negative_memory_before():
    with pytest.raises(ValueError):
        ResourceMeasurement(
            operation="intelligence",
            elapsed_seconds=0.1,
            memory_before_bytes=-1,
            memory_after_bytes=0,
        )


def test_measurement_rejects_negative_memory_after():
    with pytest.raises(ValueError):
        ResourceMeasurement(
            operation="intelligence",
            elapsed_seconds=0.1,
            memory_before_bytes=0,
            memory_after_bytes=-1,
        )


def test_budget_requires_operation():
    with pytest.raises(ValueError):
        ResourcePerformanceBudget(
            operation="",
            maximum_seconds=1.0,
            maximum_memory_growth_bytes=100,
        )


def test_budget_requires_positive_time_limit():
    with pytest.raises(ValueError):
        ResourcePerformanceBudget(
            operation="intelligence",
            maximum_seconds=0,
            maximum_memory_growth_bytes=100,
        )


def test_budget_rejects_non_integer_memory_limit():
    with pytest.raises(TypeError):
        ResourcePerformanceBudget(
            operation="intelligence",
            maximum_seconds=1.0,
            maximum_memory_growth_bytes=100.5,
        )


def test_budget_rejects_negative_memory_limit():
    with pytest.raises(ValueError):
        ResourcePerformanceBudget(
            operation="intelligence",
            maximum_seconds=1.0,
            maximum_memory_growth_bytes=-1,
        )


def test_budget_accepts_measurement_within_limits():
    budget = ResourcePerformanceBudget(
        operation="intelligence",
        maximum_seconds=1.0,
        maximum_memory_growth_bytes=1000,
    )

    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.5,
        memory_before_bytes=1000,
        memory_after_bytes=1500,
    )

    assert budget.accepts(measurement)


def test_budget_rejects_slow_operation():
    budget = ResourcePerformanceBudget(
        operation="intelligence",
        maximum_seconds=1.0,
        maximum_memory_growth_bytes=1000,
    )

    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=1.01,
        memory_before_bytes=1000,
        memory_after_bytes=1500,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_excessive_memory_growth():
    budget = ResourcePerformanceBudget(
        operation="intelligence",
        maximum_seconds=1.0,
        maximum_memory_growth_bytes=1000,
    )

    measurement = ResourceMeasurement(
        operation="intelligence",
        elapsed_seconds=0.5,
        memory_before_bytes=1000,
        memory_after_bytes=2501,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_wrong_operation():
    budget = ResourcePerformanceBudget(
        operation="intelligence",
        maximum_seconds=1.0,
        maximum_memory_growth_bytes=1000,
    )

    measurement = ResourceMeasurement(
        operation="other",
        elapsed_seconds=0.5,
        memory_before_bytes=1000,
        memory_after_bytes=1100,
    )

    assert not budget.accepts(measurement)


def test_current_process_memory_returns_non_negative_integer():
    memory = current_process_memory_bytes()

    assert isinstance(memory, int)
    assert memory >= 0


def test_measure_resource_operation_returns_result():
    result, measurement = measure_resource_operation(
        "intelligence",
        lambda: 42,
    )

    assert result == 42
    assert measurement.operation == "intelligence"


def test_measure_resource_operation_records_time():
    _, measurement = measure_resource_operation(
        "intelligence",
        lambda: None,
    )

    assert measurement.elapsed_seconds >= 0


def test_measure_resource_operation_records_memory():
    _, measurement = measure_resource_operation(
        "intelligence",
        lambda: [0] * 1000,
    )

    assert measurement.memory_before_bytes >= 0
    assert measurement.memory_after_bytes >= 0


def test_measure_resource_operation_rejects_empty_operation():
    with pytest.raises(ValueError):
        measure_resource_operation(
            "",
            lambda: None,
        )


def test_measure_resource_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_resource_operation(
            "intelligence",
            None,
        )


def test_resource_budget_targets_system_wide_intelligence():
    assert (
        SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET.operation
        == "system_wide_intelligence"
    )


def test_resource_budget_allows_256_mb_growth():
    assert (
        SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET.maximum_memory_growth_bytes
        == 256 * 1024 * 1024
    )


def test_resource_budget_accepts_normal_usage():
    measurement = ResourceMeasurement(
        operation="system_wide_intelligence",
        elapsed_seconds=1.0,
        memory_before_bytes=100 * 1024 * 1024,
        memory_after_bytes=150 * 1024 * 1024,
    )

    assert resource_usage_is_acceptable(measurement)


def test_resource_budget_rejects_excessive_usage():
    measurement = ResourceMeasurement(
        operation="system_wide_intelligence",
        elapsed_seconds=1.0,
        memory_before_bytes=100 * 1024 * 1024,
        memory_after_bytes=400 * 1024 * 1024,
    )

    assert not resource_usage_is_acceptable(measurement)
