import pytest

from engine.performance_scale_boundary import PerformanceLimits, PerformanceScaleBoundary
from engine.workload_sizing_policy import WorkloadSizingPolicy


def make_policy():
    boundary = PerformanceScaleBoundary(
        PerformanceLimits(
            max_concurrent_diagnostics=8,
            max_managed_machines=100,
            max_events_retained=500,
            max_projection_items=200,
        )
    )
    return WorkloadSizingPolicy(boundary)


def test_workload_estimate_calculates_resource_demand():
    policy = make_policy()

    estimate = policy.estimate(
        resource="concurrent_diagnostics",
        workload_size=3,
        units_per_item=2,
    )

    assert estimate.workload_size == 3
    assert estimate.units_per_item == 2
    assert estimate.estimated_demand == 6


def test_workload_is_admitted_when_estimated_demand_fits():
    decision = make_policy().evaluate(
        resource="concurrent_diagnostics",
        workload_size=3,
        current=2,
    )

    assert decision.status == "ADMITTED"
    assert decision.admitted is True
    assert decision.estimated_demand == 3
    assert decision.available_capacity == 6
    assert decision.reason == "WITHIN_CAPACITY"


def test_workload_is_rejected_when_estimated_demand_exceeds_capacity():
    decision = make_policy().evaluate(
        resource="concurrent_diagnostics",
        workload_size=7,
        current=3,
    )

    assert decision.status == "REJECTED"
    assert decision.admitted is False
    assert decision.estimated_demand == 7
    assert decision.available_capacity == 5
    assert decision.reason == "REQUEST_EXCEEDS_AVAILABLE_CAPACITY"


def test_per_item_cost_is_included_in_capacity_decision():
    decision = make_policy().evaluate(
        resource="concurrent_diagnostics",
        workload_size=3,
        units_per_item=2,
    )

    assert decision.estimated_demand == 6
    assert decision.status == "ADMITTED"


def test_zero_sized_workload_is_admitted_without_consuming_capacity():
    decision = make_policy().evaluate(
        resource="managed_machines",
        workload_size=0,
        current=100,
    )

    assert decision.status == "ADMITTED"
    assert decision.estimated_demand == 0
    assert decision.available_capacity == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"resource": "unknown", "workload_size": 1},
        {"resource": "managed_machines", "workload_size": -1},
        {"resource": "managed_machines", "workload_size": True},
        {"resource": "managed_machines", "workload_size": 1.5},
        {"resource": "managed_machines", "workload_size": 1, "units_per_item": 0},
        {"resource": "managed_machines", "workload_size": 1, "units_per_item": -2},
        {"resource": "managed_machines", "workload_size": 1, "units_per_item": True},
    ],
)
def test_invalid_estimates_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        make_policy().estimate(**kwargs)


def test_projection_describes_policy_without_executing_work():
    projection = make_policy().projection()

    assert projection["schema_version"] == "1.0"
    assert "concurrent_diagnostics" in projection["resource_units"]
    assert projection["execution_performed"] is False


def test_capacity_decisions_do_not_change_policy_configuration():
    policy = make_policy()
    before = policy.projection()

    policy.evaluate(
        resource="managed_machines",
        workload_size=10,
        current=20,
    )

    assert policy.projection() == before


def test_workload_decision_projection_is_detached():
    decision = make_policy().evaluate(
        resource="managed_machines",
        workload_size=5,
    )

    first = decision.projection()
    first["status"] = "CORRUPTED"

    assert decision.projection()["status"] == "ADMITTED"
