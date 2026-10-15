import pytest

from engine.fleet import Fleet
from engine.fleet_health_intelligence import FleetHealthIntelligence
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


def make_fleet():
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

    return fleet


def test_health_intelligence_requires_fleet():
    with pytest.raises(ValueError):
        FleetHealthIntelligence(None)


def test_health_intelligence_uses_canonical_fleet():
    fleet = Fleet("Production Fleet")

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.fleet is fleet
    assert intelligence.health.fleet is fleet


def test_empty_fleet_health_intelligence_is_unknown():
    fleet = Fleet("Empty Fleet")

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.machine_count == 0
    assert intelligence.overall_state() == "UNKNOWN"
    assert intelligence.affected_machine_count() == 0
    assert intelligence.health_concentration() == "EMPTY"
    assert intelligence.technician_attention_required() is False


def test_counts_and_percentages_are_composed_from_canonical_health():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.counts() == {
        "HEALTHY": 1,
        "WARNING": 1,
        "UNKNOWN": 1,
    }

    assert intelligence.percentages() == {
        "HEALTHY": pytest.approx(33.3333333333),
        "WARNING": pytest.approx(33.3333333333),
        "UNKNOWN": pytest.approx(33.3333333333),
    }


def test_overall_state_is_composed_from_canonical_health():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.overall_state() == "WARNING"


def test_affected_machine_count_excludes_healthy_machines():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.affected_machine_count() == 2


def test_health_percentages_are_exposed():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.healthy_percentage() == pytest.approx(
        33.3333333333
    )
    assert intelligence.warning_percentage() == pytest.approx(
        33.3333333333
    )
    assert intelligence.unknown_percentage() == pytest.approx(
        33.3333333333
    )


def test_mixed_health_is_reported_as_mixed():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.health_concentration() == "MIXED"


def test_all_healthy_fleet_has_healthy_concentration():
    fleet = Fleet("Healthy Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "HEALTHY")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "HEALTHY")
    )

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.overall_state() == "HEALTHY"
    assert intelligence.health_concentration() == "HEALTHY"
    assert intelligence.affected_machine_count() == 0
    assert intelligence.technician_attention_required() is False


def test_warning_only_fleet_requires_attention():
    fleet = Fleet("Warning Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "WARNING")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002", "WARNING")
    )

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.overall_state() == "WARNING"
    assert intelligence.health_concentration() == "WARNING"
    assert intelligence.affected_machine_count() == 2
    assert intelligence.technician_attention_required() is True


def test_unknown_only_fleet_requires_attention():
    fleet = Fleet("Unknown Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001", "UNKNOWN")
    )

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.overall_state() == "UNKNOWN"
    assert intelligence.health_concentration() == "UNKNOWN"
    assert intelligence.affected_machine_count() == 1
    assert intelligence.technician_attention_required() is True


def test_affected_machines_contains_only_warning_and_unknown():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.affected_machines() == [
        {
            "machine_id": "MACHINE-002",
            "hostname": "PC-002",
            "health_state": "WARNING",
        },
        {
            "machine_id": "MACHINE-003",
            "hostname": "PC-003",
            "health_state": "UNKNOWN",
        },
    ]


def test_affected_machines_are_defensive():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    affected = intelligence.affected_machines()
    affected[0]["health_state"] = "HEALTHY"

    assert intelligence.affected_machines()[0]["health_state"] == "WARNING"


def test_projection_contains_complete_health_intelligence_surface():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    projection = intelligence.projection()

    assert set(projection) == {
        "machine_count",
        "overall_state",
        "counts",
        "percentages",
        "affected_machine_count",
        "healthy_percentage",
        "warning_percentage",
        "unknown_percentage",
        "health_concentration",
        "technician_attention_required",
        "affected_machines",
    }

    assert projection["machine_count"] == 3
    assert projection["overall_state"] == "WARNING"
    assert projection["affected_machine_count"] == 2
    assert projection["health_concentration"] == "MIXED"
    assert projection["technician_attention_required"] is True


def test_projection_is_defensive():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    projection = intelligence.projection()
    projection["counts"]["WARNING"] = 999
    projection["affected_machines"][0]["health_state"] = "HEALTHY"

    fresh = intelligence.projection()

    assert fresh["counts"]["WARNING"] == 1
    assert fresh["affected_machines"][0]["health_state"] == "WARNING"


def test_health_intelligence_does_not_mutate_fleet():
    fleet = make_fleet()

    before = fleet.summary

    intelligence = FleetHealthIntelligence(fleet)
    intelligence.projection()

    assert fleet.summary == before


def test_health_intelligence_has_no_diagnostic_or_remediation_lifecycle():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    forbidden = {
        "diagnose",
        "diagnose_machine",
        "create_case",
        "authorize_remediation",
        "execute_remediation",
        "verify_remediation",
        "start_recovery_cycle",
    }

    assert forbidden.isdisjoint(dir(intelligence))


def test_health_intelligence_does_not_create_a_second_fleet():
    fleet = make_fleet()

    intelligence = FleetHealthIntelligence(fleet)

    assert intelligence.fleet is fleet
    assert len(
        {
            id(intelligence.fleet),
            id(intelligence.health.fleet),
        }
    ) == 1
