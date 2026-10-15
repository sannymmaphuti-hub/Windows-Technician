from copy import deepcopy

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine
from engine.fleet_technician_projection import FleetTechnicianProjection


def make_fleet():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        ManagedMachine(
            machine_id="M001",
            hostname="PC-001",
            platform="Windows",
            operating_system="Windows 11",
        )
    )
    fleet.add_machine(
        ManagedMachine(
            machine_id="M002",
            hostname="PC-002",
            platform="Windows",
            operating_system="Windows 11",
        )
    )

    return fleet


def make_case(machine_id):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.signals = [
        {
            "name": "CPU_HIGH",
        }
    ]
    case.findings = [
        {
            "finding_type": "CPU_PRESSURE",
            "severity": "HIGH",
        }
    ]

    return case


def snapshot(fleet, cases):
    return {
        "fleet_id": fleet.fleet_id,
        "name": fleet.name,
        "machines": [
            {
                "machine_id": machine.machine_id,
                "hostname": machine.hostname,
                "platform": machine.platform,
                "operating_system": machine.operating_system,
            }
            for machine in fleet.machines
        ],
        "cases": [
            {
                "case_id": case.case_id,
                "machine_id": case.machine_id,
                "signals": deepcopy(case.signals),
                "findings": deepcopy(case.findings),
                "recommendations": deepcopy(case.recommendations),
            }
            for case in cases
        ],
    }


def test_projection_does_not_expose_remediation_controls():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    )

    assert not hasattr(projection, "authorize_remediation")
    assert not hasattr(projection, "execute_remediation")
    assert not hasattr(projection, "verify_remediation")


def test_projection_does_not_mutate_fleet_or_cases():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    before = snapshot(fleet, cases)

    result = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert result

    after = snapshot(fleet, cases)

    assert after == before


def test_projection_is_defensive():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    projection["fleet"]["name"] = "MUTATED"
    projection["overview"]["cases"]["case_count"] = 999
    projection["attention"]["priority_counts"]["HIGH"] = 999

    fresh = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert fresh["fleet"]["name"] == "Production Fleet"
    assert fresh["overview"]["cases"]["case_count"] != 999
    assert fresh["attention"]["priority_counts"].get("HIGH") != 999


def test_projection_is_deterministic():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    first = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    second = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert first == second


def test_projection_contains_no_execution_state():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    serialized = repr(projection).upper()

    assert "EXECUTED" not in serialized
    assert "AUTHORIZED" not in serialized
    assert "REMEDIATING" not in serialized


def test_projection_remains_observational():
    fleet = make_fleet()
    cases = [
        make_case("M001"),
    ]

    result = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert set(result) == {
        "fleet",
        "overview",
        "attention",
        "investigation",
        "intelligence",
    }


def test_only_supplied_cases_are_projected():
    fleet = make_fleet()

    cases = [
        make_case("M001"),
    ]

    result = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert result["overview"]["cases"]["case_count"] == 1
    assert result["overview"]["cases"]["affected_machine_ids"] == [
        "M001"
    ]
