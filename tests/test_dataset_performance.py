"""Tests for large diagnostic dataset performance boundaries."""

import pytest

from packaging.dataset_performance import (
    DatasetPerformanceBudget,
    DatasetPerformanceMeasurement,
    LARGE_DATASET_BUDGET,
    NORMAL_DATASET_BUDGET,
    STRESS_DATASET_BUDGET,
    diagnostic_dataset_is_acceptable,
    measure_dataset_operation,
)


def test_measurement_stores_operation():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.operation == "diagnostic"


def test_measurement_stores_item_count():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.item_count == 100


def test_measurement_converts_to_milliseconds():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.elapsed_milliseconds == 100.0


def test_measurement_calculates_throughput():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=1000,
        elapsed_seconds=0.5,
    )

    assert measurement.items_per_second == 2000.0


def test_measurement_zero_time_has_infinite_throughput():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=0.0,
    )

    assert measurement.items_per_second == float("inf")


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        DatasetPerformanceMeasurement(
            operation="",
            item_count=100,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_non_integer_item_count():
    with pytest.raises(TypeError):
        DatasetPerformanceMeasurement(
            operation="diagnostic",
            item_count=100.5,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_item_count():
    with pytest.raises(ValueError):
        DatasetPerformanceMeasurement(
            operation="diagnostic",
            item_count=-1,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_elapsed_time():
    with pytest.raises(ValueError):
        DatasetPerformanceMeasurement(
            operation="diagnostic",
            item_count=100,
            elapsed_seconds=-0.1,
        )


def test_budget_rejects_empty_operation():
    with pytest.raises(ValueError):
        DatasetPerformanceBudget(
            operation="",
            maximum_seconds=1.0,
            minimum_item_count=100,
        )


def test_budget_rejects_non_positive_limit():
    with pytest.raises(ValueError):
        DatasetPerformanceBudget(
            operation="diagnostic",
            maximum_seconds=0,
            minimum_item_count=100,
        )


def test_budget_rejects_negative_item_count():
    with pytest.raises(ValueError):
        DatasetPerformanceBudget(
            operation="diagnostic",
            maximum_seconds=1.0,
            minimum_item_count=-1,
        )


def test_budget_accepts_matching_measurement():
    budget = DatasetPerformanceBudget(
        operation="diagnostic",
        maximum_seconds=1.0,
        minimum_item_count=100,
    )

    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=0.5,
    )

    assert budget.accepts(measurement)


def test_budget_rejects_wrong_operation():
    budget = DatasetPerformanceBudget(
        operation="diagnostic",
        maximum_seconds=1.0,
        minimum_item_count=100,
    )

    measurement = DatasetPerformanceMeasurement(
        operation="other",
        item_count=100,
        elapsed_seconds=0.5,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_too_few_items():
    budget = DatasetPerformanceBudget(
        operation="diagnostic",
        maximum_seconds=1.0,
        minimum_item_count=100,
    )

    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=99,
        elapsed_seconds=0.1,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_slow_operation():
    budget = DatasetPerformanceBudget(
        operation="diagnostic",
        maximum_seconds=1.0,
        minimum_item_count=100,
    )

    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic",
        item_count=100,
        elapsed_seconds=1.01,
    )

    assert not budget.accepts(measurement)


def test_measure_dataset_operation_processes_dataset():
    dataset = list(range(100))

    result, measurement = measure_dataset_operation(
        "diagnostic",
        dataset,
        lambda items: sum(items),
    )

    assert result == sum(dataset)
    assert measurement.item_count == 100


def test_measure_dataset_operation_accepts_generators():
    dataset = (value for value in range(100))

    result, measurement = measure_dataset_operation(
        "diagnostic",
        dataset,
        lambda items: len(items),
    )

    assert result == 100
    assert measurement.item_count == 100


def test_measure_dataset_operation_passes_materialized_list():
    dataset = range(100)

    captured = []

    def operation(items):
        captured.append(items)
        return len(items)

    result, _ = measure_dataset_operation(
        "diagnostic",
        dataset,
        operation,
    )

    assert result == 100
    assert isinstance(captured[0], list)


def test_measure_dataset_operation_rejects_empty_operation():
    with pytest.raises(ValueError):
        measure_dataset_operation(
            "",
            range(10),
            lambda items: None,
        )


def test_measure_dataset_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_dataset_operation(
            "diagnostic",
            range(10),
            None,
        )


def test_normal_budget_targets_100_items():
    assert NORMAL_DATASET_BUDGET.minimum_item_count == 100


def test_large_budget_targets_1000_items():
    assert LARGE_DATASET_BUDGET.minimum_item_count == 1000


def test_stress_budget_targets_10000_items():
    assert STRESS_DATASET_BUDGET.minimum_item_count == 10000


def test_normal_dataset_is_acceptable():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic_dataset_processing",
        item_count=100,
        elapsed_seconds=0.1,
    )

    assert diagnostic_dataset_is_acceptable(measurement)


def test_large_dataset_is_acceptable():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic_dataset_processing",
        item_count=1000,
        elapsed_seconds=0.5,
    )

    assert diagnostic_dataset_is_acceptable(measurement)


def test_stress_dataset_is_acceptable():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic_dataset_processing",
        item_count=10000,
        elapsed_seconds=4.0,
    )

    assert diagnostic_dataset_is_acceptable(measurement)


def test_stress_dataset_rejects_slow_processing():
    measurement = DatasetPerformanceMeasurement(
        operation="diagnostic_dataset_processing",
        item_count=10000,
        elapsed_seconds=5.01,
    )

    assert not diagnostic_dataset_is_acceptable(measurement)
