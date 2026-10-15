import pytest

from engine.performance_scale_boundary import (
    CapacityDecision,
    PerformanceLimits,
    PerformanceScaleBoundary,
)


def test_default_performance_limits_are_explicit():
    boundary = PerformanceScaleBoundary()

    result = boundary.projection()

    assert result["schema_version"] == "1.0"
    assert result["limits"]["max_concurrent_diagnostics"] == 8
    assert result["limits"]["max_managed_machines"] == 500
    assert result["limits"]["max_events_retained"] == 10_000
    assert result["limits"]["max_projection_items"] == 1_000
    assert result["execution_performed"] is False


def test_capacity_is_admitted_when_request_fits():
    boundary = PerformanceScaleBoundary(
        PerformanceLimits(max_concurrent_diagnostics=8)
    )

    result = boundary.evaluate_capacity(
        resource="concurrent_diagnostics",
        requested=3,
        current=2,
    )

    assert isinstance(result, CapacityDecision)
    assert result.admitted is True
    assert result.available == 6
    assert result.reason == "WITHIN_CAPACITY"


def test_capacity_is_rejected_when_request_exceeds_budget():
    boundary = PerformanceScaleBoundary(
        PerformanceLimits(max_concurrent_diagnostics=8)
    )

    result = boundary.evaluate_capacity(
        resource="concurrent_diagnostics",
        requested=7,
        current=3,
    )

    assert result.admitted is False
    assert result.available == 5
    assert result.reason == "REQUEST_EXCEEDS_AVAILABLE_CAPACITY"


def test_capacity_is_rejected_when_budget_is_exhausted():
    boundary = PerformanceScaleBoundary(
        PerformanceLimits(max_managed_machines=10)
    )

    result = boundary.evaluate_capacity(
        resource="managed_machines",
        requested=1,
        current=10,
    )

    assert result.admitted is False
    assert result.available == 0
    assert result.reason == "CAPACITY_EXHAUSTED"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_concurrent_diagnostics": 0},
        {"max_managed_machines": -1},
        {"max_events_retained": True},
        {"max_projection_items": 1.5},
    ],
)
def test_invalid_performance_limits_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        PerformanceLimits(**kwargs)


@pytest.mark.parametrize(
    "requested,current",
    [
        (-1, 0),
        (1, -1),
        (True, 0),
        (1, False),
        (1.5, 0),
    ],
)
def test_invalid_capacity_inputs_are_rejected(requested, current):
    boundary = PerformanceScaleBoundary()

    with pytest.raises((TypeError, ValueError)):
        boundary.evaluate_capacity(
            resource="concurrent_diagnostics",
            requested=requested,
            current=current,
        )


def test_unknown_resource_is_rejected():
    boundary = PerformanceScaleBoundary()

    with pytest.raises(ValueError, match="Unsupported resource"):
        boundary.evaluate_capacity(
            resource="unknown",
            requested=1,
        )


def test_capacity_evaluation_does_not_change_configured_limits():
    boundary = PerformanceScaleBoundary()
    before = boundary.projection()

    boundary.evaluate_capacity(
        resource="concurrent_diagnostics",
        requested=100,
    )

    assert boundary.projection() == before


def test_projection_is_independent_between_reads():
    boundary = PerformanceScaleBoundary()

    first = boundary.projection()
    first["limits"]["max_managed_machines"] = 999_999

    second = boundary.projection()

    assert second["limits"]["max_managed_machines"] == 500
