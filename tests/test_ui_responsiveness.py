"""Tests for UI responsiveness performance boundaries."""

import pytest

from packaging.ui_responsiveness import (
    DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET,
    UI_INTERACTION_PERFORMANCE_BUDGET,
    UI_STATE_UPDATE_PERFORMANCE_BUDGET,
    UIResponsivenessBudget,
    UIResponsivenessMeasurement,
    dashboard_refresh_is_responsive,
    measure_ui_operation,
    ui_interaction_is_responsive,
    ui_state_update_is_responsive,
)


def test_measurement_stores_operation():
    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert measurement.operation == "interaction"


def test_measurement_stores_elapsed_time():
    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert measurement.elapsed_seconds == 0.05


def test_measurement_converts_to_milliseconds():
    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert measurement.elapsed_milliseconds == 50.0


def test_measurement_stores_completion_state():
    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert measurement.completed is True


def test_measurement_rejects_empty_operation():
    with pytest.raises(ValueError):
        UIResponsivenessMeasurement(
            operation="",
            elapsed_seconds=0.05,
            completed=True,
        )


def test_measurement_rejects_negative_elapsed_time():
    with pytest.raises(ValueError):
        UIResponsivenessMeasurement(
            operation="interaction",
            elapsed_seconds=-0.01,
            completed=True,
        )


def test_measurement_rejects_invalid_completion_state():
    with pytest.raises(TypeError):
        UIResponsivenessMeasurement(
            operation="interaction",
            elapsed_seconds=0.05,
            completed=1,
        )


def test_budget_rejects_empty_operation():
    with pytest.raises(ValueError):
        UIResponsivenessBudget(
            operation="",
            maximum_seconds=0.1,
        )


def test_budget_requires_positive_limit():
    with pytest.raises(ValueError):
        UIResponsivenessBudget(
            operation="interaction",
            maximum_seconds=0,
        )


def test_budget_accepts_completed_fast_operation():
    budget = UIResponsivenessBudget(
        operation="interaction",
        maximum_seconds=0.1,
    )

    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert budget.accepts(measurement)


def test_budget_rejects_slow_operation():
    budget = UIResponsivenessBudget(
        operation="interaction",
        maximum_seconds=0.1,
    )

    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.11,
        completed=True,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_incomplete_operation():
    budget = UIResponsivenessBudget(
        operation="interaction",
        maximum_seconds=0.1,
    )

    measurement = UIResponsivenessMeasurement(
        operation="interaction",
        elapsed_seconds=0.01,
        completed=False,
    )

    assert not budget.accepts(measurement)


def test_budget_rejects_wrong_operation():
    budget = UIResponsivenessBudget(
        operation="interaction",
        maximum_seconds=0.1,
    )

    measurement = UIResponsivenessMeasurement(
        operation="other",
        elapsed_seconds=0.01,
        completed=True,
    )

    assert not budget.accepts(measurement)


def test_measure_ui_operation_returns_result():
    result, measurement = measure_ui_operation(
        "interaction",
        lambda: 42,
    )

    assert result == 42
    assert measurement.completed is True


def test_measure_ui_operation_records_elapsed_time():
    _, measurement = measure_ui_operation(
        "interaction",
        lambda: None,
    )

    assert measurement.elapsed_seconds >= 0


def test_measure_ui_operation_rejects_empty_operation():
    with pytest.raises(ValueError):
        measure_ui_operation(
            "",
            lambda: None,
        )


def test_measure_ui_operation_rejects_non_callable():
    with pytest.raises(TypeError):
        measure_ui_operation(
            "interaction",
            None,
        )


def test_measure_ui_operation_preserves_exception():
    def failing_operation():
        raise RuntimeError("expected failure")

    with pytest.raises(RuntimeError):
        measure_ui_operation(
            "interaction",
            failing_operation,
        )


def test_interaction_budget_is_100_milliseconds():
    assert (
        UI_INTERACTION_PERFORMANCE_BUDGET.maximum_seconds
        == 0.1
    )


def test_state_update_budget_is_100_milliseconds():
    assert (
        UI_STATE_UPDATE_PERFORMANCE_BUDGET.maximum_seconds
        == 0.1
    )


def test_dashboard_refresh_budget_is_250_milliseconds():
    assert (
        DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET.maximum_seconds
        == 0.25
    )


def test_fast_ui_interaction_is_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="ui_interaction",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert ui_interaction_is_responsive(measurement)


def test_slow_ui_interaction_is_not_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="ui_interaction",
        elapsed_seconds=0.101,
        completed=True,
    )

    assert not ui_interaction_is_responsive(measurement)


def test_fast_state_update_is_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="ui_state_update",
        elapsed_seconds=0.05,
        completed=True,
    )

    assert ui_state_update_is_responsive(measurement)


def test_slow_state_update_is_not_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="ui_state_update",
        elapsed_seconds=0.101,
        completed=True,
    )

    assert not ui_state_update_is_responsive(measurement)


def test_fast_dashboard_refresh_is_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="dashboard_refresh",
        elapsed_seconds=0.2,
        completed=True,
    )

    assert dashboard_refresh_is_responsive(measurement)


def test_slow_dashboard_refresh_is_not_responsive():
    measurement = UIResponsivenessMeasurement(
        operation="dashboard_refresh",
        elapsed_seconds=0.251,
        completed=True,
    )

    assert not dashboard_refresh_is_responsive(measurement)
