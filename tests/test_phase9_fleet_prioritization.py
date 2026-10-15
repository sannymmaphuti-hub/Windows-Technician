import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_prioritization import FleetPrioritization
from engine.managed_machine import ManagedMachine
from engine.recommendation import Recommendation


def make_fleet():
    fleet = Fleet("Production Fleet")

    for machine_id in ("M001", "M002", "M003"):
        fleet.add_machine(
            ManagedMachine(
                machine_id=machine_id,
                hostname=f"PC-{machine_id[-3:]}",
                platform="Windows",
                operating_system="Windows 11",
            )
        )

    return fleet


def make_case(machine_id, recommendations):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.recommendations = list(recommendations)
    return case


def recommendation(
    recommendation_type,
    priority,
    category="system",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category=category,
        priority=priority,
        description=f"Investigate {recommendation_type}.",
        rationale="Fleet intelligence evidence.",
    )


def test_requires_fleet():
    with pytest.raises(ValueError):
        FleetPrioritization("not-a-fleet")


def test_requires_cases_list_or_tuple():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetPrioritization(
            fleet,
            cases="invalid",
        )


def test_requires_diagnostic_cases():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetPrioritization(
            fleet,
            cases=["invalid"],
        )


def test_empty_projection():
    fleet = make_fleet()

    prioritization = FleetPrioritization(fleet)

    projection = prioritization.projection()

    assert projection["summary"]["recommendation_count"] == 0
    assert projection["summary"]["top_recommendation_key"] is None
    assert projection["summary"]["top_score"] is None
    assert projection["ranked_recommendations"] == []
    assert projection["top_recommendation"] is None


def test_single_recommendation_is_ranked():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [
            recommendation(
                "memory_review",
                "HIGH",
            )
        ],
    )

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    ranked = prioritization.ranked_recommendations()

    assert len(ranked) == 1
    assert ranked[0]["rank"] == 1
    assert ranked[0]["recommendation_key"] == "memory_review"


def test_critical_priority_outranks_low_priority_when_impact_is_equal():
    fleet = make_fleet()

    low = make_case(
        "M001",
        [recommendation("low_issue", "LOW")],
    )

    critical = make_case(
        "M002",
        [recommendation("critical_issue", "CRITICAL")],
    )

    prioritization = FleetPrioritization(
        fleet,
        [low, critical],
    )

    ranked = prioritization.ranked_recommendations()

    assert ranked[0]["recommendation_key"] == "critical_issue"
    assert ranked[1]["recommendation_key"] == "low_issue"


def test_more_affected_machines_increases_score():
    fleet = make_fleet()

    one_machine = make_case(
        "M001",
        [recommendation("one_machine", "MEDIUM")],
    )

    two_machine_a = make_case(
        "M002",
        [recommendation("two_machine", "MEDIUM")],
    )

    two_machine_b = make_case(
        "M003",
        [recommendation("two_machine", "MEDIUM")],
    )

    prioritization = FleetPrioritization(
        fleet,
        [
            one_machine,
            two_machine_a,
            two_machine_b,
        ],
    )

    ranked = prioritization.ranked_recommendations()

    scores = {
        item["recommendation_key"]:
            item["scoring"]["total_score"]
        for item in ranked
    }

    assert scores["two_machine"] > scores["one_machine"]


def test_recurrence_increases_score():
    fleet = make_fleet()

    recurring_a = make_case(
        "M001",
        [recommendation("recurring_issue", "MEDIUM")],
    )

    recurring_b = make_case(
        "M002",
        [recommendation("recurring_issue", "MEDIUM")],
    )

    single = make_case(
        "M003",
        [recommendation("single_issue", "MEDIUM")],
    )

    prioritization = FleetPrioritization(
        fleet,
        [
            recurring_a,
            recurring_b,
            single,
        ],
    )

    ranked = prioritization.ranked_recommendations()

    scores = {
        item["recommendation_key"]:
            item["scoring"]["total_score"]
        for item in ranked
    }

    assert scores["recurring_issue"] > scores["single_issue"]


def test_fleet_wide_recommendation_receives_bonus():
    fleet = make_fleet()

    cases = [
        make_case(
            machine_id,
            [
                recommendation(
                    "fleet_issue",
                    "MEDIUM",
                )
            ],
        )
        for machine_id in (
            "M001",
            "M002",
            "M003",
        )
    ]

    prioritization = FleetPrioritization(
        fleet,
        cases,
    )

    ranked = prioritization.ranked_recommendations()

    assert ranked[0]["recommendation_key"] == "fleet_issue"
    assert ranked[0]["scoring"]["fleet_wide"] is True
    assert ranked[0]["scoring"]["fleet_wide_bonus"] == 25


def test_priority_counts_are_aggregated():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [recommendation("a", "HIGH")],
        ),
        make_case(
            "M002",
            [recommendation("b", "HIGH")],
        ),
        make_case(
            "M003",
            [recommendation("c", "LOW")],
        ),
    ]

    prioritization = FleetPrioritization(
        fleet,
        cases,
    )

    assert prioritization.priority_counts() == {
        "HIGH": 2,
        "LOW": 1,
    }


def test_unknown_priority_is_supported_for_projection():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [
            {
                "recommendation_type": "unknown_issue",
                "category": "system",
                "description": "Unknown priority issue.",
                "rationale": "Test.",
            }
        ],
    )

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    ranked = prioritization.ranked_recommendations()

    assert ranked[0]["scoring"]["priority"] == "UNKNOWN"
    assert prioritization.priority_counts() == {
        "UNKNOWN": 1,
    }


def test_affected_machine_ids_are_unique_and_ordered():
    fleet = make_fleet()

    cases = [
        make_case(
            "M002",
            [recommendation("a", "LOW")],
        ),
        make_case(
            "M001",
            [recommendation("b", "LOW")],
        ),
        make_case(
            "M002",
            [recommendation("c", "LOW")],
        ),
    ]

    prioritization = FleetPrioritization(
        fleet,
        cases,
    )

    assert prioritization.affected_machine_ids() == [
        "M002",
        "M001",
    ]


def test_cases_outside_fleet_are_excluded():
    fleet = make_fleet()

    case = make_case(
        "OUTSIDE",
        [recommendation("outside_issue", "CRITICAL")],
    )

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    assert prioritization.ranked_recommendations() == []


def test_top_recommendation_matches_rank_one():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [recommendation("top_issue", "HIGH")],
    )

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    top = prioritization.top_recommendation()

    assert top["rank"] == 1
    assert top["recommendation_key"] == "top_issue"


def test_projection_has_canonical_keys():
    fleet = make_fleet()

    prioritization = FleetPrioritization(fleet)

    assert set(
        prioritization.projection().keys()
    ) == {
        "fleet",
        "summary",
        "affected_machine_ids",
        "priority_counts",
        "ranked_recommendations",
        "top_recommendation",
    }


def test_projection_is_defensive():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [
            recommendation(
                "memory_review",
                "HIGH",
            )
        ],
    )

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    projection = prioritization.projection()

    projection["ranked_recommendations"][0][
        "machine_ids"
    ].append("MUTATED")

    fresh = prioritization.projection()

    assert "MUTATED" not in fresh[
        "ranked_recommendations"
    ][0]["machine_ids"]


def test_does_not_mutate_cases():
    fleet = make_fleet()

    original = recommendation(
        "memory_review",
        "HIGH",
    )

    case = make_case(
        "M001",
        [original],
    )

    before = list(case.recommendations)

    prioritization = FleetPrioritization(
        fleet,
        [case],
    )

    prioritization.projection()

    assert case.recommendations == before


def test_no_remediation_lifecycle_methods():
    fleet = make_fleet()

    prioritization = FleetPrioritization(fleet)

    forbidden = {
        "authorize_remediation",
        "execute_remediation",
        "verify_remediation",
        "remediate",
        "diagnose",
    }

    assert not (
        forbidden
        & set(dir(prioritization))
    )
