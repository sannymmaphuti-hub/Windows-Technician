from copy import deepcopy

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_technician_projection import (
    FleetTechnicianProjection,
)
from engine.managed_machine import ManagedMachine
from engine.recommendation import Recommendation


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


def make_case(
    machine_id,
    signals=None,
    findings=None,
    root_causes=None,
    recommendations=None,
):
    case = DiagnosticCase()
    case.machine_id = machine_id

    case.signals = list(signals or [])
    case.findings = list(findings or [])
    case.root_causes = list(root_causes or [])
    case.recommendations = list(
        recommendations or []
    )

    return case


def make_recommendation(
    recommendation_type,
    priority="HIGH",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category="SYSTEM",
        priority=priority,
        description=(
            f"Investigate {recommendation_type}"
        ),
        rationale="Fleet evidence indicates attention is required.",
    )


def test_constructor_requires_fleet():
    with pytest.raises(ValueError):
        FleetTechnicianProjection(
            "not-a-fleet"
        )


def test_constructor_requires_case_collection():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetTechnicianProjection(
            fleet,
            "not-a-list",
        )


def test_constructor_requires_diagnostic_cases():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetTechnicianProjection(
            fleet,
            [object()],
        )


def test_projection_has_canonical_top_level_surface():
    fleet = make_fleet()

    projection = FleetTechnicianProjection(
        fleet
    ).projection()

    assert set(projection.keys()) == {
        "fleet",
        "overview",
        "attention",
        "investigation",
        "intelligence",
    }


def test_projection_identifies_fleet():
    fleet = make_fleet()

    projection = FleetTechnicianProjection(
        fleet
    ).projection()

    assert projection["fleet"] == {
        "fleet_id": fleet.fleet_id,
        "name": fleet.name,
    }


def test_empty_fleet_projection_is_deterministic():
    fleet = make_fleet()

    first = FleetTechnicianProjection(
        fleet
    ).projection()

    second = FleetTechnicianProjection(
        fleet
    ).projection()

    assert first == second


def test_projection_contains_all_existing_intelligence_domains():
    fleet = make_fleet()

    projection = FleetTechnicianProjection(
        fleet
    ).projection()

    assert set(
        projection["intelligence"].keys()
    ) == {
        "health",
        "cases",
        "signals",
        "findings",
        "root_causes",
        "recommendations",
        "prioritization",
        "anomalies",
    }


def test_overview_contains_health_and_case_intelligence():
    fleet = make_fleet()

    cases = [
        make_case("M001"),
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert "health" in projection["overview"]
    assert "cases" in projection["overview"]


def test_attention_exposes_prioritization_and_anomalies():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
            findings=[{"finding_type": "CPU_PRESSURE"}],
            recommendations=[
                make_recommendation("CPU_REVIEW")
            ],
        )
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    attention = projection["attention"]

    assert "top_recommendation" in attention
    assert "ranked_recommendations" in attention
    assert "machine_outliers" in attention
    assert "signal_outliers" in attention
    assert "finding_outliers" in attention
    assert "recommendation_outliers" in attention


def test_investigation_exposes_existing_intelligence():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
            findings=[{"finding_type": "CPU_PRESSURE"}],
            root_causes=[
                {
                    "cause_type": "RESOURCE_PRESSURE"
                }
            ],
            recommendations=[
                make_recommendation("CPU_REVIEW")
            ],
        )
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    investigation = projection["investigation"]

    assert "signals" in investigation
    assert "findings" in investigation
    assert "root_causes" in investigation
    assert "recommendations" in investigation


def test_projection_does_not_mutate_cases():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
            findings=[{"finding_type": "CPU_PRESSURE"}],
            recommendations=[
                make_recommendation("CPU_REVIEW")
            ],
        )
    ]

    before = deepcopy(cases[0].__dict__)

    FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert cases[0].__dict__ == before


def test_projection_returns_defensive_copies():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
        )
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    projection["investigation"]["signals"].clear()

    second = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    assert second["investigation"]["signals"]


def test_projection_is_deterministic_for_same_input():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
            findings=[{"finding_type": "CPU_PRESSURE"}],
            recommendations=[
                make_recommendation("CPU_REVIEW")
            ],
        ),
        make_case(
            "M002",
            signals=[{"name": "MEMORY_HIGH"}],
            findings=[{"finding_type": "MEMORY_PRESSURE"}],
            recommendations=[
                make_recommendation(
                    "MEMORY_REVIEW",
                    priority="MEDIUM",
                )
            ],
        ),
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


def test_projection_preserves_machine_scope():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "CPU_HIGH"}],
        ),
        make_case(
            "NOT-A-FLEET-MACHINE",
            signals=[{"name": "SHOULD_NOT_APPEAR"}],
        ),
    ]

    projection = FleetTechnicianProjection(
        fleet,
        cases,
    ).projection()

    signal_projection = (
        projection["investigation"]["signals"]
    )

    assert "SHOULD_NOT_APPEAR" not in str(
        signal_projection
    )
