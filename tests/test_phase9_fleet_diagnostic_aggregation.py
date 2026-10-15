import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_diagnostic_aggregation import FleetDiagnosticAggregation
from engine.managed_machine import ManagedMachine


def make_machine(machine_id, hostname):
    return ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )


def make_case(
    machine_id,
    *,
    observations=None,
    signals=None,
    findings=None,
    correlations=None,
    root_causes=None,
    recommendations=None,
    lifecycle_state="DIAGNOSED",
):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.lifecycle_state = lifecycle_state

    case.set_observations(
        observations if observations is not None else []
    )
    case.set_signals(
        signals if signals is not None else []
    )
    case.set_findings(
        findings if findings is not None else []
    )
    case.set_correlations(
        correlations if correlations is not None else []
    )
    case.set_root_causes(
        root_causes if root_causes is not None else []
    )
    case.set_recommendations(
        recommendations if recommendations is not None else []
    )

    return case


def make_fleet():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    return fleet


def test_requires_fleet():
    with pytest.raises(ValueError):
        FleetDiagnosticAggregation(None)


def test_requires_diagnostic_cases():
    fleet = make_fleet()

    with pytest.raises(ValueError):
        FleetDiagnosticAggregation(
            fleet,
            cases=["not a case"],
        )


def test_only_cases_belonging_to_fleet_are_aggregated():
    fleet = make_fleet()

    fleet_case = make_case("MACHINE-001")
    external_case = make_case("MACHINE-999")

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [fleet_case, external_case],
    )

    assert aggregation.case_count == 1
    assert aggregation.cases[0] is fleet_case


def test_affected_machine_ids_are_unique_and_ordered():
    fleet = make_fleet()

    first = make_case("MACHINE-001")
    second = make_case("MACHINE-001")
    third = make_case("MACHINE-002")

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [first, second, third],
    )

    assert aggregation.affected_machine_ids == [
        "MACHINE-001",
        "MACHINE-002",
    ]
    assert aggregation.affected_machine_count == 2


def test_diagnostic_counts_aggregate_canonical_case_surfaces():
    fleet = make_fleet()

    first = make_case(
        "MACHINE-001",
        observations=["o1", "o2"],
        signals=["s1"],
        findings=[{"finding": "memory"}],
        correlations=["c1", "c2"],
        root_causes=[{"cause": "memory_pressure"}],
        recommendations=["r1"],
    )

    second = make_case(
        "MACHINE-002",
        observations=["o3"],
        signals=["s2", "s3"],
        findings=[{"finding": "cpu"}],
        correlations=["c3"],
        root_causes=[{"cause": "cpu_pressure"}],
        recommendations=["r2", "r3"],
    )

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [first, second],
    )

    assert aggregation.observation_count() == 3
    assert aggregation.signal_count() == 3
    assert aggregation.finding_count() == 2
    assert aggregation.correlation_count() == 3
    assert aggregation.root_cause_count() == 2
    assert aggregation.recommendation_count() == 3


def test_empty_fleet_has_zero_diagnostic_counts():
    fleet = Fleet("Empty Fleet")

    aggregation = FleetDiagnosticAggregation(fleet)

    assert aggregation.case_count == 0
    assert aggregation.affected_machine_count == 0
    assert aggregation.observation_count() == 0
    assert aggregation.signal_count() == 0
    assert aggregation.finding_count() == 0
    assert aggregation.correlation_count() == 0
    assert aggregation.root_cause_count() == 0
    assert aggregation.recommendation_count() == 0


def test_case_diagnostic_surface_contains_canonical_counts():
    fleet = make_fleet()

    case = make_case(
        "MACHINE-001",
        observations=["o1"],
        signals=["s1", "s2"],
        findings=["f1"],
        correlations=["c1"],
        root_causes=["r1", "r2"],
        recommendations=["rec1"],
    )

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [case],
    )

    assert aggregation.case_diagnostic_surface() == [
        {
            "case_id": case.case_id,
            "machine_id": "MACHINE-001",
            "hostname": None,
            "lifecycle_state": "DIAGNOSED",
            "diagnostic_completeness": "INCOMPLETE",
            "status": "NORMAL",
            "observation_count": 1,
            "signal_count": 2,
            "finding_count": 1,
            "correlation_count": 1,
            "root_cause_count": 2,
            "recommendation_count": 1,
        }
    ]


def test_case_diagnostic_surface_is_defensive():
    fleet = make_fleet()

    case = make_case(
        "MACHINE-001",
        findings=["finding"],
    )

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [case],
    )

    surface = aggregation.case_diagnostic_surface()
    surface[0]["finding_count"] = 999

    assert (
        aggregation.case_diagnostic_surface()[0]["finding_count"]
        == 1
    )


def test_projection_contains_complete_diagnostic_surface():
    fleet = make_fleet()

    case = make_case(
        "MACHINE-001",
        observations=["o1"],
        signals=["s1"],
        findings=["f1"],
        correlations=["c1"],
        root_causes=["r1"],
        recommendations=["r1"],
    )

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [case],
    )

    projection = aggregation.projection()

    assert set(projection) == {
        "case_count",
        "affected_machine_count",
        "affected_machine_ids",
        "observation_count",
        "signal_count",
        "finding_count",
        "correlation_count",
        "root_cause_count",
        "recommendation_count",
        "cases",
    }

    assert projection["case_count"] == 1
    assert projection["affected_machine_count"] == 1
    assert projection["observation_count"] == 1
    assert projection["signal_count"] == 1
    assert projection["finding_count"] == 1
    assert projection["correlation_count"] == 1
    assert projection["root_cause_count"] == 1
    assert projection["recommendation_count"] == 1


def test_projection_is_defensive():
    fleet = make_fleet()

    case = make_case(
        "MACHINE-001",
        findings=["f1"],
    )

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [case],
    )

    projection = aggregation.projection()

    projection["affected_machine_ids"].append(
        "MACHINE-999"
    )
    projection["cases"][0]["finding_count"] = 999

    fresh = aggregation.projection()

    assert fresh["affected_machine_ids"] == [
        "MACHINE-001"
    ]
    assert fresh["cases"][0]["finding_count"] == 1


def test_aggregation_does_not_mutate_cases_or_fleet():
    fleet = make_fleet()

    case = make_case(
        "MACHINE-001",
        findings=["f1"],
    )

    before_findings = list(case.findings)
    before_machine_ids = list(fleet.machine_ids)

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [case],
    )
    aggregation.projection()

    assert case.findings == before_findings
    assert fleet.machine_ids == before_machine_ids


def test_aggregation_has_no_diagnostic_or_remediation_lifecycle():
    fleet = make_fleet()

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [make_case("MACHINE-001")],
    )

    forbidden = {
        "diagnose",
        "diagnose_machine",
        "create_case",
        "authorize_remediation",
        "execute_remediation",
        "verify_remediation",
        "start_recovery_cycle",
    }

    assert forbidden.isdisjoint(dir(aggregation))


def test_aggregation_reuses_same_fleet_identity():
    fleet = make_fleet()

    aggregation = FleetDiagnosticAggregation(
        fleet,
        [make_case("MACHINE-001")],
    )

    assert aggregation.fleet is fleet
