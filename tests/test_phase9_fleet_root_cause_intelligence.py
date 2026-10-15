from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_root_cause_intelligence import FleetRootCauseIntelligence
from engine.managed_machine import ManagedMachine


def make_fleet():
    fleet = Fleet("Production Fleet")

    for machine_id, hostname in (
        ("M001", "PC-001"),
        ("M002", "PC-002"),
        ("M003", "PC-003"),
    ):
        fleet.add_machine(
            ManagedMachine(
                machine_id=machine_id,
                hostname=hostname,
                platform="Windows",
                operating_system="Windows 11",
            )
        )

    return fleet


def make_case(machine_id, root_causes):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.root_causes = list(root_causes)
    return case


def test_requires_fleet():
    try:
        FleetRootCauseIntelligence(object())
        assert False
    except ValueError:
        pass


def test_requires_diagnostic_cases():
    try:
        FleetRootCauseIntelligence(
            make_fleet(),
            [object()],
        )
        assert False
    except ValueError:
        pass


def test_empty_projection():
    result = FleetRootCauseIntelligence(
        make_fleet()
    ).projection()

    assert result["summary"]["unique_root_cause_count"] == 0
    assert result["summary"]["total_root_cause_occurrences"] == 0
    assert result["affected_machine_ids"] == []


def test_aggregates_unique_root_causes():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M002",
            [{"cause_type": "DISK_PRESSURE"}],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["summary"]["unique_root_cause_count"] == 2


def test_recurring_root_cause_spans_multiple_machines():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M002",
            [{"cause_type": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M003",
            [{"cause_type": "DISK_PRESSURE"}],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    assert (
        "MEMORY_PRESSURE"
        in result["recurring_root_causes"]
    )

    assert (
        "DISK_PRESSURE"
        not in result["recurring_root_causes"]
    )


def test_tracks_root_cause_occurrences():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M002",
            [{"cause_type": "MEMORY_PRESSURE"}],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    entry = result[
        "root_cause_occurrences"
    ]["MEMORY_PRESSURE"]

    assert entry["occurrence_count"] == 2
    assert entry["machine_ids"] == [
        "M001",
        "M002",
    ]
    assert len(entry["case_ids"]) == 2


def test_tracks_confidence_values():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{
                "cause_type": "MEMORY_PRESSURE",
                "confidence": 0.9,
            }],
        ),
        make_case(
            "M002",
            [{
                "cause_type": "MEMORY_PRESSURE",
                "confidence": 0.8,
            }],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    entry = result[
        "root_cause_occurrences"
    ]["MEMORY_PRESSURE"]

    assert entry["confidence_values"] == [
        0.9,
        0.8,
    ]


def test_machine_root_causes():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{
                "cause_type": "MEMORY_PRESSURE",
                "confidence": 0.9,
            }],
        ),
        make_case(
            "M002",
            [{
                "cause_type": "DISK_PRESSURE",
                "confidence": 0.7,
            }],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    assert len(
        result["machine_root_causes"]["M001"]
    ) == 1

    assert (
        result["machine_root_causes"]["M001"][0]
        ["root_cause_key"]
        == "MEMORY_PRESSURE"
    )


def test_affected_machine_ids():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "A"}],
        ),
        make_case("M002", []),
        make_case(
            "M003",
            [{"cause_type": "B"}],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["affected_machine_ids"] == [
        "M001",
        "M003",
    ]


def test_excludes_cases_outside_fleet():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "A"}],
        ),
        make_case(
            "OUTSIDE",
            [{"cause_type": "A"}],
        ),
    ]

    result = FleetRootCauseIntelligence(
        fleet,
        cases,
    ).projection()

    assert (
        result["summary"]
        ["total_root_cause_occurrences"]
        == 1
    )


def test_projection_is_defensive():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"cause_type": "A"}],
        )
    ]

    aggregation = FleetRootCauseIntelligence(
        fleet,
        cases,
    )

    projection = aggregation.projection()

    projection[
        "root_cause_occurrences"
    ]["A"]["machine_ids"].append(
        "MUTATED"
    )

    fresh = aggregation.projection()

    assert "MUTATED" not in (
        fresh[
            "root_cause_occurrences"
        ]["A"]["machine_ids"]
    )


def test_does_not_mutate_cases():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [{"cause_type": "A"}],
    )

    original = list(case.root_causes)

    FleetRootCauseIntelligence(
        fleet,
        [case],
    ).projection()

    assert case.root_causes == original


def test_projection_surface():
    result = FleetRootCauseIntelligence(
        make_fleet()
    ).projection()

    assert set(result.keys()) == {
        "fleet",
        "summary",
        "affected_machine_ids",
        "root_cause_occurrences",
        "recurring_root_causes",
        "machine_root_causes",
    }


def test_no_diagnostic_or_remediation_lifecycle():
    aggregation = FleetRootCauseIntelligence(
        make_fleet()
    )

    assert not hasattr(aggregation, "diagnose")
    assert not hasattr(aggregation, "execute")
    assert not hasattr(aggregation, "authorize")
    assert not hasattr(aggregation, "remediate")
    assert not hasattr(aggregation, "verify")
