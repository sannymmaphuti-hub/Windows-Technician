import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation
from engine.managed_machine import ManagedMachine


def make_machine(machine_id, hostname):
    return ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )


def make_case(machine_id, state):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.lifecycle_state = state
    return case


def test_case_aggregation_requires_fleet():
    with pytest.raises(ValueError):
        FleetCaseAggregation(None)


def test_case_aggregation_requires_diagnostic_cases():
    fleet = Fleet("Production Fleet")

    with pytest.raises(ValueError):
        FleetCaseAggregation(
            fleet,
            cases=["not a case"],
        )


def test_only_cases_belonging_to_fleet_are_projected():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    fleet_case = make_case(
        "MACHINE-001",
        "OPEN",
    )

    external_case = make_case(
        "MACHINE-999",
        "OPEN",
    )

    aggregation = FleetCaseAggregation(
        fleet,
        [fleet_case, external_case],
    )

    assert aggregation.case_count == 1
    assert aggregation.cases[0] is fleet_case


def test_active_cases_use_canonical_lifecycle_states():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    open_case = make_case(
        "MACHINE-001",
        "OPEN",
    )

    resolved_case = make_case(
        "MACHINE-001",
        "RESOLVED",
    )

    aggregation = FleetCaseAggregation(
        fleet,
        [open_case, resolved_case],
    )

    assert aggregation.active_case_count == 1
    assert aggregation.active_cases()[0]["case_id"] == open_case.case_id


def test_unresolved_cases_exclude_terminal_cases():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    investigating = make_case(
        "MACHINE-001",
        "INVESTIGATING",
    )

    closed = make_case(
        "MACHINE-001",
        "CLOSED",
    )

    aggregation = FleetCaseAggregation(
        fleet,
        [investigating, closed],
    )

    assert aggregation.unresolved_case_count == 1
    assert (
        aggregation.unresolved_cases()[0]["case_id"]
        == investigating.case_id
    )


def test_cases_by_machine_groups_fleet_cases():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    first = make_case("MACHINE-001", "OPEN")
    second = make_case("MACHINE-001", "INVESTIGATING")
    third = make_case("MACHINE-002", "DIAGNOSED")

    aggregation = FleetCaseAggregation(
        fleet,
        [first, second, third],
    )

    grouped = aggregation.cases_by_machine()

    assert set(grouped) == {
        "MACHINE-001",
        "MACHINE-002",
    }

    assert [
        item["case_id"]
        for item in grouped["MACHINE-001"]
    ] == [
        first.case_id,
        second.case_id,
    ]

    assert [
        item["case_id"]
        for item in grouped["MACHINE-002"]
    ] == [
        third.case_id,
    ]


def test_state_counts_reflect_fleet_cases():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    first = make_case("MACHINE-001", "OPEN")
    second = make_case("MACHINE-001", "OPEN")
    third = make_case("MACHINE-002", "RESOLVED")

    aggregation = FleetCaseAggregation(
        fleet,
        [first, second, third],
    )

    assert aggregation.state_counts() == {
        "OPEN": 2,
        "RESOLVED": 1,
    }


def test_affected_machine_ids_are_unique_and_ordered():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    first = make_case("MACHINE-001", "OPEN")
    second = make_case("MACHINE-001", "INVESTIGATING")
    third = make_case("MACHINE-002", "OPEN")

    aggregation = FleetCaseAggregation(
        fleet,
        [first, second, third],
    )

    assert aggregation.affected_machine_ids() == [
        "MACHINE-001",
        "MACHINE-002",
    ]


def test_case_projection_is_defensive():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    case = make_case(
        "MACHINE-001",
        "OPEN",
    )

    aggregation = FleetCaseAggregation(
        fleet,
        [case],
    )

    projection = aggregation.projection()

    projection["active_cases"][0]["lifecycle_state"] = "CLOSED"

    assert (
        aggregation.active_cases()[0]["lifecycle_state"]
        == "OPEN"
    )


def test_projection_contains_complete_case_surface():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    case = make_case(
        "MACHINE-001",
        "OPEN",
    )

    aggregation = FleetCaseAggregation(
        fleet,
        [case],
    )

    projection = aggregation.projection()

    assert set(projection) == {
        "case_count",
        "active_case_count",
        "unresolved_case_count",
        "affected_machine_ids",
        "state_counts",
        "active_cases",
        "unresolved_cases",
        "cases_by_machine",
    }
