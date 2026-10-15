import pytest

from engine.fleet_workload_policy import FleetWorkloadPolicy
from engine.performance_scale_boundary import PerformanceLimits
from engine.workload_sizing_policy import WorkloadSizingPolicy
from engine.performance_scale_boundary import PerformanceScaleBoundary


def make_policy(limit=8):
    sizing = WorkloadSizingPolicy(
        PerformanceScaleBoundary(
            PerformanceLimits(
                max_concurrent_diagnostics=limit,
                max_managed_machines=500,
                max_events_retained=1000,
                max_projection_items=1000,
            )
        )
    )
    return FleetWorkloadPolicy(sizing)


def test_small_fleet_workload_is_admitted():
    decision = make_policy().evaluate(fleet_size=4)
    assert decision.admitted is True
    assert decision.estimated_demand == 4


def test_fleet_over_capacity_is_rejected():
    decision = make_policy().evaluate(fleet_size=9)
    assert decision.admitted is False
    assert decision.estimated_demand == 9


def test_workload_accounts_for_units_per_machine():
    decision = make_policy().evaluate(
        fleet_size=3,
        units_per_machine=2,
    )
    assert decision.estimated_demand == 6
    assert decision.admitted is True


def test_existing_workload_reduces_available_capacity():
    decision = make_policy(limit=8).evaluate(
        fleet_size=3,
        current=6,
    )
    assert decision.admitted is False


def test_zero_sized_fleet_is_admitted_without_work():
    decision = make_policy().evaluate(fleet_size=0)
    assert decision.admitted is True
    assert decision.estimated_demand == 0


@pytest.mark.parametrize(
    ("kwargs", "exception"),
    [
        ({"fleet_size": -1}, ValueError),
        ({"fleet_size": True}, TypeError),
        ({"fleet_size": 1.5}, TypeError),
        ({"fleet_size": 1, "units_per_machine": 0}, ValueError),
        ({"fleet_size": 1, "current": -1}, ValueError),
    ],
)
def test_invalid_fleet_workloads_are_rejected(kwargs, exception):
    with pytest.raises(exception):
        FleetWorkloadPolicy().evaluate(**kwargs)


def test_projection_does_not_execute_fleet_work():
    projection = FleetWorkloadPolicy().projection()
    assert projection["policy"] == "fleet_workload_admission"
    assert projection["execution_performed"] is False
