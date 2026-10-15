from copy import deepcopy

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_recommendation_intelligence import (
    FleetRecommendationIntelligence,
)


def make_case(machine_id, hostname):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = hostname
    return case


def recommendation(
    recommendation_type,
    priority="MEDIUM",
    category="memory",
):
    return {
        "recommendation_type": recommendation_type,
        "priority": priority,
        "category": category,
        "description": (
            f"Investigate {recommendation_type}."
        ),
    }


@pytest.fixture
def fleet():
    fleet = Fleet("Production Fleet")

    from engine.managed_machine import ManagedMachine

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

    fleet.add_machine(
        ManagedMachine(
            machine_id="M003",
            hostname="PC-003",
            platform="Windows",
            operating_system="Windows 10",
        )
    )

    return fleet


def test_requires_fleet():
    intelligence = FleetRecommendationIntelligence()

    with pytest.raises(ValueError):
        intelligence.projection(
            "not-a-fleet",
            [],
        )


def test_requires_case_list_or_tuple(fleet):
    intelligence = FleetRecommendationIntelligence()

    with pytest.raises(ValueError):
        intelligence.projection(
            fleet,
            "not-a-list",
        )


def test_requires_diagnostic_cases(fleet):
    intelligence = FleetRecommendationIntelligence()

    with pytest.raises(ValueError):
        intelligence.projection(
            fleet,
            ["not-a-case"],
        )


def test_empty_projection(fleet):
    intelligence = FleetRecommendationIntelligence()

    projection = intelligence.projection(
        fleet,
        [],
    )

    assert projection["summary"] == {
        "unique_recommendation_count": 0,
        "total_recommendation_occurrences": 0,
        "recurring_recommendation_count": 0,
        "affected_machine_count": 0,
        "priority_counts": {},
    }

    assert projection["affected_machine_ids"] == []
    assert projection["recommendation_occurrences"] == {}
    assert projection["recurring_recommendations"] == {}
    assert projection["machine_recommendations"] == {}


def test_aggregates_unique_recommendations(fleet):
    case = make_case("M001", "PC-001")

    case.recommendations = [
        recommendation(
            "memory_review",
            "HIGH",
        ),
        recommendation(
            "storage_review",
            "MEDIUM",
        ),
    ]

    intelligence = FleetRecommendationIntelligence()

    occurrences = intelligence.recommendation_occurrences(
        fleet,
        [case],
    )

    assert len(occurrences) == 2
    assert all(
        entry["occurrence_count"] == 1
        for entry in occurrences.values()
    )


def test_detects_recurring_recommendation_across_machines(
    fleet,
):
    case_one = make_case("M001", "PC-001")
    case_two = make_case("M002", "PC-002")

    shared = recommendation(
        "memory_review",
        "HIGH",
    )

    case_one.recommendations = [shared]
    case_two.recommendations = [deepcopy(shared)]

    intelligence = FleetRecommendationIntelligence()

    recurring = intelligence.recurring_recommendations(
        fleet,
        [case_one, case_two],
    )

    assert len(recurring) == 1

    entry = next(iter(recurring.values()))

    assert entry["occurrence_count"] == 2
    assert entry["machine_ids"] == [
        "M001",
        "M002",
    ]


def test_tracks_case_ids(fleet):
    case_one = make_case("M001", "PC-001")
    case_two = make_case("M002", "PC-002")

    shared = recommendation("memory_review")

    case_one.recommendations = [shared]
    case_two.recommendations = [deepcopy(shared)]

    intelligence = FleetRecommendationIntelligence()

    occurrences = intelligence.recommendation_occurrences(
        fleet,
        [case_one, case_two],
    )

    entry = next(iter(occurrences.values()))

    assert entry["case_ids"] == [
        case_one.case_id,
        case_two.case_id,
    ]


def test_tracks_priority_counts(fleet):
    case_one = make_case("M001", "PC-001")
    case_two = make_case("M002", "PC-002")

    case_one.recommendations = [
        recommendation("memory_review", "HIGH"),
    ]

    case_two.recommendations = [
        recommendation("storage_review", "MEDIUM"),
        recommendation("cpu_review", "LOW"),
    ]

    intelligence = FleetRecommendationIntelligence()

    counts = intelligence.recommendation_priority_counts(
        fleet,
        [case_one, case_two],
    )

    assert counts == {
        "HIGH": 1,
        "MEDIUM": 1,
        "LOW": 1,
    }


def test_missing_priority_becomes_unknown(fleet):
    case = make_case("M001", "PC-001")

    case.recommendations = [
        {
            "recommendation_type": "memory_review",
        }
    ]

    intelligence = FleetRecommendationIntelligence()

    counts = intelligence.recommendation_priority_counts(
        fleet,
        [case],
    )

    assert counts == {
        "UNKNOWN": 1,
    }


def test_tracks_affected_machines(fleet):
    case_one = make_case("M001", "PC-001")
    case_two = make_case("M002", "PC-002")

    case_one.recommendations = [
        recommendation("memory_review")
    ]

    case_two.recommendations = []

    intelligence = FleetRecommendationIntelligence()

    assert intelligence.affected_machine_ids(
        fleet,
        [case_one, case_two],
    ) == ["M001"]


def test_machine_recommendations_are_grouped_by_machine(
    fleet,
):
    case = make_case("M001", "PC-001")

    case.recommendations = [
        recommendation("memory_review", "HIGH"),
        recommendation("storage_review", "MEDIUM"),
    ]

    intelligence = FleetRecommendationIntelligence()

    result = intelligence.machine_recommendations(
        fleet,
        [case],
    )

    assert list(result) == ["M001"]
    assert len(result["M001"]) == 2
    assert {
        item["priority"]
        for item in result["M001"]
    } == {
        "HIGH",
        "MEDIUM",
    }


def test_excludes_cases_outside_fleet(fleet):
    fleet_case = make_case("M001", "PC-001")
    outside_case = make_case("OUTSIDE", "OTHER-PC")

    fleet_case.recommendations = [
        recommendation("memory_review")
    ]

    outside_case.recommendations = [
        recommendation("outside_problem")
    ]

    intelligence = FleetRecommendationIntelligence()

    projection = intelligence.projection(
        fleet,
        [fleet_case, outside_case],
    )

    assert projection[
        "affected_machine_ids"
    ] == ["M001"]

    assert projection[
        "summary"
    ]["unique_recommendation_count"] == 1


def test_projection_is_defensive(fleet):
    case = make_case("M001", "PC-001")

    case.recommendations = [
        recommendation("memory_review")
    ]

    intelligence = FleetRecommendationIntelligence()

    projection = intelligence.projection(
        fleet,
        [case],
    )

    key = next(
        iter(
            projection[
                "recommendation_occurrences"
            ]
        )
    )

    projection[
        "recommendation_occurrences"
    ][key]["machine_ids"].append(
        "MUTATED"
    )

    fresh = intelligence.projection(
        fleet,
        [case],
    )

    assert "MUTATED" not in fresh[
        "recommendation_occurrences"
    ][key]["machine_ids"]


def test_projection_does_not_mutate_cases(fleet):
    case = make_case("M001", "PC-001")

    case.recommendations = [
        recommendation("memory_review")
    ]

    before = deepcopy(
        case.recommendations
    )

    intelligence = FleetRecommendationIntelligence()

    intelligence.projection(
        fleet,
        [case],
    )

    assert case.recommendations == before


def test_projection_has_canonical_keys(fleet):
    intelligence = FleetRecommendationIntelligence()

    projection = intelligence.projection(
        fleet,
        [],
    )

    assert set(projection) == {
        "fleet",
        "summary",
        "affected_machine_ids",
        "recommendation_priority_counts",
        "recommendation_occurrences",
        "recurring_recommendations",
        "machine_recommendations",
    }


def test_existing_generate_surface_remains_available():
    intelligence = FleetRecommendationIntelligence()

    assert hasattr(
        intelligence,
        "generate",
    )


def test_no_remediation_lifecycle_methods():
    intelligence = FleetRecommendationIntelligence()

    forbidden = {
        "authorize",
        "execute",
        "verify",
        "remediate",
    }

    assert not any(
        hasattr(intelligence, name)
        for name in forbidden
    )
