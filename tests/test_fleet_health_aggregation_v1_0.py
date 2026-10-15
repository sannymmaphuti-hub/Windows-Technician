import pytest

from engine.fleet import Fleet
from engine.fleet_health_aggregation import FleetHealthAggregation
from engine.managed_machine import ManagedMachine


def make_machine(
    machine_id,
    hostname,
    health_state="HEALTHY",
):
    machine = ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )
    machine.health_state = health_state
    return machine


def test_health_aggregation_requires_fleet():
    with pytest.raises(ValueError):
        FleetHealthAggregation(None)


def test_empty_fleet_has_unknown_overall_state():
    fleet = Fleet("Empty Fleet")

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.machine_count == 0
    assert aggregation.counts() == {
        "HEALTHY": 0,
        "WARNING": 0,
        "UNKNOWN": 0,
    }
    assert aggregation.overall_state() == "UNKNOWN"


def test_health_counts_match_canonical_machine_states():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "WARNING")
    )
    fleet.add_machine(
        make_machine("MACHINE-003", "PC-003", "UNKNOWN")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.counts() == {
        "HEALTHY": 1,
        "WARNING": 1,
        "UNKNOWN": 1,
    }


def test_health_percentages_reflect_fleet_membership():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-003", "PC-003", "WARNING")
    )
    fleet.add_machine(
        make_machine("MACHINE-004", "PC-004", "UNKNOWN")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.percentages() == {
        "HEALTHY": 50.0,
        "WARNING": 25.0,
        "UNKNOWN": 25.0,
    }


def test_warning_is_overall_state_when_any_machine_is_warning():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "WARNING")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.overall_state() == "WARNING"


def test_unknown_is_overall_state_when_no_warning_exists_but_unknown_exists():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "UNKNOWN")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.overall_state() == "UNKNOWN"


def test_all_healthy_machines_produce_healthy_overall_state():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "HEALTHY")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.overall_state() == "HEALTHY"


def test_unknown_health_values_are_normalized_to_unknown():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "DEGRADED")
    )

    aggregation = FleetHealthAggregation(fleet)

    assert aggregation.counts() == {
        "HEALTHY": 0,
        "WARNING": 0,
        "UNKNOWN": 1,
    }

    assert aggregation.machine_breakdown() == [
        {
            "machine_id": "MACHINE-001",
            "hostname": "PC-001",
            "health_state": "UNKNOWN",
        }
    ]


def test_machine_breakdown_is_defensive():
    fleet = Fleet("Production Fleet")
    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )

    aggregation = FleetHealthAggregation(fleet)

    breakdown = aggregation.machine_breakdown()
    breakdown[0]["health_state"] = "WARNING"

    assert aggregation.machine_breakdown()[0]["health_state"] == "HEALTHY"


def test_projection_contains_complete_health_surface():
    fleet = Fleet("Production Fleet")
    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )

    aggregation = FleetHealthAggregation(fleet)

    projection = aggregation.projection()

    assert set(projection) == {
        "machine_count",
        "overall_state",
        "counts",
        "percentages",
        "machines",
    }
    assert projection["machine_count"] == 1
    assert projection["overall_state"] == "HEALTHY"
