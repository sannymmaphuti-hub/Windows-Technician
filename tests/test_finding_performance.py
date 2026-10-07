"""Tests for many-findings performance boundaries."""

import pytest

from packaging.finding_performance import (
    FindingPerformanceBudget,
    FindingPerformanceMeasurement,
    LARGE_FINDINGS_BUDGET,
    NORMAL_FINDINGS_BUDGET,
    STRESS_FINDINGS_BUDGET,
    finding_processing_is_acceptable,
    measure_finding_operation,
)


def test_measurement_stores_operation():
    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.operation == "findings"


def test_measurement_stores_finding_count():
    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.finding_count == 100


def test_measurement_converts_to_milliseconds():
    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=0.1,
    )

    assert measurement.elapsed_milliseconds == 100.0


def test_measurement_calculates_findings_per_second():
    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=1000,
        elapsed_seconds=0.5,
    )

    assert measurement.findings_per_second == 2000.0


def test_zero_elapsed_time_reports_infinite_throughput():
    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=0.0,
    )

    assert measurement.findings_per_second == float("inf")


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        FindingPerformanceMeasurement(
            operation="",
            finding_count=100,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_non_integer_count():
    with pytest.raises(TypeError):
        FindingPerformanceMeasurement(
            operation="findings",
            finding_count=100.5,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_count():
    with pytest.raises(ValueError):
        FindingPerformanceMeasurement(
            operation="findings",
            finding_count=-1,
            elapsed_seconds=0.1,
        )


def test_measurement_rejects_negative_elapsed_time():
    with pytest.raises(ValueError):
        FindingPerformanceMeasurement(
            operation="findings",
            finding_count=100,
            elapsed_seconds=-0.1,
        )


def test_budget_rejects_empty_operation():
    with pytest.raises(ValueError):
        FindingPerformanceBudget(
            operation="",
            maximum_seconds=1.0,
            minimum_finding_count=100,
        )


def test_budget_rejects_non_positive_limit():
    with pytest.raises(ValueError):
        FindingPerformanceBudget(
            operation="findings",
            maximum_seconds=0,
            minimum_finding_count=100,
        )


def test_budget_rejects_negative_minimum():
    with pytest.raises(ValueError):
        FindingPerformanceBudget(
            operation="findings",
            maximum_seconds=1.0,
            minimum_finding_count=-1,
        )


def test_budget_accepts_matching_measurement():
    budget = FindingPerformanceBudget(
        operation="findings",
        maximum_seconds=1.0,
        minimum_finding_count=100,
    )

    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=0.5,
    )

    assert budget.accepts(measurement)


def test_budget_rejects_wrong_operation():
    budget = FindingPerformanceBudget(
        operation="findings",
        maximum_seconds=1.0,
        minimum_finding_count=100,
    )

    measurement = FindingPerformanceMeasurement(
        operation="other",
        finding_count=100,
        elapsed_seconds=0.5,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_too_few_findings():
    budget = FindingPerformanceBudget(
        operation="findings",
        maximum_seconds=1.0,
        minimum_finding_count=100,
    )

    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=99,
        elapsed_seconds=0.1,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_slow_processing():
    budget = FindingPerformanceBudget(
        operation="findings",
        maximum_seconds=1.0,
        minimum_finding_count=100,
    )

    measurement = FindingPerformanceMeasurement(
        operation="findings",
        finding_count=100,
        elapsed_seconds=1.01,
    )

    assert not budget.accepts(measurement)


def test_measure_finding_operation_processes_findings():
    findings = list(range(100))

    result, measurement = measure_finding_operation(
        "findings",
        findings,
        lambda items: len(items),
    )

    assert result == 100
    assert measurement.finding_count == 100


def test_measure_finding_operation_accepts_generator():
    findings = (value for value in range(100))

    result, measurement = measure_finding_operation(
        "findings",
        findings,
        lambda items: len(items),
    )

    assert result == 100
    assert measurement.finding_count == 100


def test_measure_finding_operation_passes_list_to_callback():
    captured = []

    def operation(items):
        captured.append(items)
        return len(items)

    result, _ = measure_finding_operation(
        "findings",
        range(100),
        operation,
    )

    assert result == 100
    assert isinstance(captured[0], list)


def test_measure_finding_operation_rejects_empty_operation():
    with pytest.raises(ValueError):
        measure_finding_operation(
            "",
            range(10),
            lambda items: None,
        )


def test_measure_finding_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_finding_operation(
            "findings",
            range(10),
            None,
        )


def test_normal_budget_targets_100_findings():
    assert NORMAL_FINDINGS_BUDGET.minimum_finding_count == 100


def test_large_budget_targets_1000_findings():
    assert LARGE_FINDINGS_BUDGET.minimum_finding_count == 1000


def test_stress_budget_targets_10000_findings():
    assert STRESS_FINDINGS_BUDGET.minimum_finding_count == 10000


def test_normal_processing_is_acceptable():
    measurement = FindingPerformanceMeasurement(
        operation="finding_processing",
        finding_count=100,
        elapsed_seconds=0.1,
    )

    assert finding_processing_is_acceptable(measurement)


def test_large_processing_is_acceptable():
    measurement = FindingPerformanceMeasurement(
        operation="finding_processing",
        finding_count=1000,
        elapsed_seconds=0.5,
    )

    assert finding_processing_is_acceptable(measurement)


def test_stress_processing_is_acceptable():
    measurement = FindingPerformanceMeasurement(
        operation="finding_processing",
        finding_count=10000,
        elapsed_seconds=4.0,
    )

    assert finding_processing_is_acceptable(measurement)


def test_stress_processing_rejects_slow_operation():
    measurement = FindingPerformanceMeasurement(
        operation="finding_processing",
        finding_count=10000,
        elapsed_seconds=5.01,
    )

    assert not finding_processing_is_acceptable(measurement)
