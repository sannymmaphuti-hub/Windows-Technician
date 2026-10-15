from copy import deepcopy

import pytest

from engine.fleet import Fleet
from engine.fleet_intelligence_boundary import FleetIntelligenceBoundary


def build_fleet():
    return Fleet("Test Fleet")


def test_boundary_requires_fleet():
    with pytest.raises(ValueError):
        FleetIntelligenceBoundary(object())


def test_boundary_stores_canonical_fleet():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    assert boundary.fleet is fleet


def test_boundary_exposes_inventory_projection():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.inventory_projection()

    assert result is not None


def test_boundary_exposes_health_projection():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.health_projection()

    assert result is not None


def test_boundary_exposes_case_projection():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.case_projection()

    assert result is not None


def test_boundary_exposes_alert_projection():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.alert_projection()

    assert result is not None


def test_projection_contains_canonical_fleet_identity():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.projection()

    assert result["fleet"]["fleet_id"] == fleet.fleet_id
    assert result["fleet"]["name"] == "Test Fleet"


def test_projection_contains_all_canonical_inputs():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    result = boundary.projection()

    assert "inventory" in result
    assert "health" in result
    assert "cases" in result
    assert "alerts" in result


def test_projection_is_defensively_copied():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    first = boundary.projection()
    second = boundary.projection()

    assert first == second
    assert first is not second


def test_nested_projection_mutation_does_not_change_boundary():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    first = boundary.projection()

    first["fleet"]["fleet_id"] = "tampered"

    second = boundary.projection()

    assert second["fleet"]["fleet_id"] == fleet.fleet_id


def test_boundary_does_not_mutate_fleet():
    fleet = build_fleet()

    before = deepcopy(fleet.__dict__)

    boundary = FleetIntelligenceBoundary(fleet)
    boundary.projection()

    assert fleet.__dict__ == before


def test_boundary_is_read_only():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    before = deepcopy(fleet.__dict__)

    boundary.inventory_projection()
    boundary.health_projection()
    boundary.case_projection()
    boundary.alert_projection()
    boundary.projection()

    assert fleet.__dict__ == before


def test_boundary_has_no_diagnostic_lifecycle():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    assert not hasattr(boundary, "diagnose")
    assert not hasattr(boundary, "execute_remediation")
    assert not hasattr(boundary, "authorize_remediation")
    assert not hasattr(boundary, "verify_remediation")


def test_boundary_does_not_create_second_fleet():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    assert boundary.fleet is fleet


def test_projection_is_stable_across_reads():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    first = boundary.projection()
    second = boundary.projection()

    assert first == second


def test_component_boundaries_are_owned_by_same_fleet():
    fleet = build_fleet()

    boundary = FleetIntelligenceBoundary(fleet)

    assert boundary.inventory.fleet is fleet
    assert boundary.health.fleet is fleet
    assert boundary.cases.fleet is fleet
    assert boundary.alerts.fleet is fleet
