import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_anomaly_intelligence import FleetAnomalyIntelligence
from engine.managed_machine import ManagedMachine
from engine.recommendation import Recommendation


def make_fleet():
    fleet = Fleet("Production Fleet")

    for machine_id in (
        "M001",
        "M002",
        "M003",
        "M004",
    ):
        fleet.add_machine(
            ManagedMachine(
                machine_id=machine_id,
                hostname=f"PC-{machine_id[-3:]}",
                platform="Windows",
                operating_system="Windows 11",
            )
        )

    return fleet


def make_case(
    machine_id,
    signals=None,
    findings=None,
    recommendations=None,
):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.signals = list(signals or [])
    case.findings = list(findings or [])
    case.recommendations = list(
        recommendations or []
    )
    return case


def make_recommendation(
    recommendation_type,
    priority="MEDIUM",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category="system",
        priority=priority,
        description=f"Investigate {recommendation_type}.",
        rationale="Fleet intelligence evidence.",
    )


def test_requires_fleet():
    with pytest.raises(ValueError):
        FleetAnomalyIntelligence("invalid")


def test_requires_cases_list_or_tuple():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetAnomalyIntelligence(
            fleet,
            cases="invalid",
        )


def test_requires_diagnostic_cases():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetAnomalyIntelligence(
            fleet,
            cases=["invalid"],
        )


def test_empty_projection():
    fleet = make_fleet()

    intelligence = FleetAnomalyIntelligence(fleet)

    projection = intelligence.projection()

    assert projection["summary"] == {
        "signal_outlier_count": 0,
        "finding_outlier_count": 0,
        "recommendation_outlier_count": 0,
        "machine_outlier_count": 0,
    }

    assert projection["signal_outliers"] == {}
    assert projection["finding_outliers"] == {}
    assert projection["recommendation_outliers"] == {}
    assert projection["machine_outliers"] == {}


def test_machine_activity_counts_are_aggregated():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=["S1", "S2"],
            findings=["F1"],
            recommendations=[
                make_recommendation("R1")
            ],
        ),
        make_case(
            "M001",
            signals=["S3"],
            findings=["F2", "F3"],
            recommendations=[],
        ),
        make_case(
            "M002",
            signals=["S1"],
        ),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    activity = intelligence.machine_activity()

    assert activity["M001"] == {
        "case_count": 2,
        "signal_count": 3,
        "finding_count": 3,
        "recommendation_count": 1,
    }

    assert activity["M002"]["case_count"] == 1
    assert activity["M003"]["case_count"] == 0


def test_signal_distribution_tracks_machines_and_occurrences():
    fleet = make_fleet()

    cases = [
        make_case("M001", signals=[{"name": "RAM_HIGH"}]),
        make_case("M002", signals=[{"name": "RAM_HIGH"}]),
        make_case("M003", signals=[{"name": "CPU_HIGH"}]),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    distribution = intelligence.signal_distribution()

    assert distribution["RAM_HIGH"]["occurrence_count"] == 2
    assert distribution["RAM_HIGH"]["machine_ids"] == [
        "M001",
        "M002",
    ]


def test_signal_outlier_is_detected_when_less_than_half_fleet_is_affected():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "DISK_FAILURE"}],
        ),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    outliers = intelligence.signal_outliers()

    assert "DISK_FAILURE" in outliers
    assert outliers["DISK_FAILURE"][
        "affected_machine_count"
    ] == 1
    assert outliers["DISK_FAILURE"][
        "machine_ratio"
    ] == 0.25


def test_signal_affecting_half_fleet_is_not_an_outlier():
    fleet = make_fleet()

    cases = [
        make_case("M001", signals=[{"name": "RAM_HIGH"}]),
        make_case("M002", signals=[{"name": "RAM_HIGH"}]),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    assert intelligence.signal_outliers() == {}


def test_finding_outlier_is_detected():
    fleet = make_fleet()

    cases = [
        make_case(
            "M004",
            findings=[{"finding_type": "DISK_PRESSURE"}],
        ),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    assert "DISK_PRESSURE" in (
        intelligence.finding_outliers()
    )


def test_recommendation_outlier_is_detected():
    fleet = make_fleet()

    cases = [
        make_case(
            "M003",
            recommendations=[
                make_recommendation(
                    "memory_review"
                )
            ],
        ),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    assert "memory_review" in (
        intelligence.recommendation_outliers()
    )


def test_machine_outlier_is_detected_from_case_activity():
    fleet = make_fleet()

    cases = [
        make_case("M001"),
        make_case("M001"),
        make_case("M001"),
        make_case("M002"),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    outliers = intelligence.machine_outliers()

    assert "M001" in outliers
    assert outliers["M001"]["case_count"] == 3
    assert outliers["M001"]["deviation"] > 0


def test_machine_with_average_activity_is_not_an_outlier():
    fleet = make_fleet()

    cases = [
        make_case("M001"),
        make_case("M002"),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    assert intelligence.machine_outliers() == {}


def test_outside_fleet_cases_are_excluded():
    fleet = make_fleet()

    case = make_case(
        "OUTSIDE",
        signals=[{"name": "CRITICAL_SIGNAL"}],
        findings=[{"finding_type": "CRITICAL_FINDING"}],
        recommendations=[
            make_recommendation(
                "critical_issue",
                "CRITICAL",
            )
        ],
    )

    intelligence = FleetAnomalyIntelligence(
        fleet,
        [case],
    )

    assert intelligence.signal_distribution() == {}
    assert intelligence.finding_distribution() == {}
    assert intelligence.recommendation_distribution() == {}


def test_projection_has_canonical_keys():
    fleet = make_fleet()

    intelligence = FleetAnomalyIntelligence(fleet)

    assert set(
        intelligence.projection().keys()
    ) == {
        "fleet",
        "summary",
        "machine_activity",
        "signal_distribution",
        "finding_distribution",
        "recommendation_distribution",
        "signal_outliers",
        "finding_outliers",
        "recommendation_outliers",
        "machine_outliers",
    }


def test_projection_is_defensive():
    fleet = make_fleet()

    case = make_case(
        "M001",
        signals=[{"name": "RAM_HIGH"}],
    )

    intelligence = FleetAnomalyIntelligence(
        fleet,
        [case],
    )

    projection = intelligence.projection()

    projection["signal_distribution"]["RAM_HIGH"][
        "machine_ids"
    ].append("MUTATED")

    fresh = intelligence.projection()

    assert "MUTATED" not in fresh[
        "signal_distribution"
    ]["RAM_HIGH"]["machine_ids"]


def test_does_not_mutate_cases():
    fleet = make_fleet()

    signal = {"name": "RAM_HIGH"}
    finding = {"finding_type": "MEMORY_PRESSURE"}
    rec = make_recommendation("memory_review")

    case = make_case(
        "M001",
        signals=[signal],
        findings=[finding],
        recommendations=[rec],
    )

    before_signals = list(case.signals)
    before_findings = list(case.findings)
    before_recommendations = list(
        case.recommendations
    )

    intelligence = FleetAnomalyIntelligence(
        fleet,
        [case],
    )

    intelligence.projection()

    assert case.signals == before_signals
    assert case.findings == before_findings
    assert case.recommendations == before_recommendations


def test_no_diagnostic_or_remediation_lifecycle():
    fleet = make_fleet()

    intelligence = FleetAnomalyIntelligence(fleet)

    forbidden = {
        "diagnose",
        "authorize_remediation",
        "execute_remediation",
        "verify_remediation",
        "remediate",
    }

    assert not (
        forbidden
        & set(dir(intelligence))
    )


def test_anomaly_summary_matches_detected_anomalies():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            signals=[{"name": "S1"}],
            findings=[{"finding_type": "F1"}],
            recommendations=[
                make_recommendation("R1")
            ],
        ),
        make_case("M001"),
        make_case("M001"),
    ]

    intelligence = FleetAnomalyIntelligence(
        fleet,
        cases,
    )

    summary = intelligence.anomaly_summary()

    assert summary["signal_outlier_count"] == 1
    assert summary["finding_outlier_count"] == 1
    assert summary["recommendation_outlier_count"] == 1
    assert summary["machine_outlier_count"] == 1
