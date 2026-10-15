from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_finding_intelligence import FleetFindingIntelligence
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


def make_case(machine_id, findings):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.findings = list(findings)
    return case


def test_requires_fleet():
    try:
        FleetFindingIntelligence(object())
        assert False
    except ValueError:
        pass


def test_requires_diagnostic_cases():
    try:
        FleetFindingIntelligence(
            make_fleet(),
            [object()],
        )
        assert False
    except ValueError:
        pass


def test_empty_projection():
    result = FleetFindingIntelligence(
        make_fleet()
    ).projection()

    assert result["summary"]["unique_finding_count"] == 0
    assert result["summary"]["total_finding_occurrences"] == 0
    assert result["affected_machine_ids"] == []


def test_aggregates_unique_findings():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M002",
            [{"name": "DISK_PRESSURE"}],
        ),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["summary"]["unique_finding_count"] == 2


def test_recurring_finding_spans_multiple_machines():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M002",
            [{"name": "MEMORY_PRESSURE"}],
        ),
        make_case(
            "M003",
            [{"name": "DISK_PRESSURE"}],
        ),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert "MEMORY_PRESSURE" in result["recurring_findings"]
    assert "DISK_PRESSURE" not in result["recurring_findings"]


def test_tracks_finding_occurrences():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "MEMORY_PRESSURE", "severity": "HIGH"}],
        ),
        make_case(
            "M002",
            [{"name": "MEMORY_PRESSURE", "severity": "HIGH"}],
        ),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    entry = result["finding_occurrences"]["MEMORY_PRESSURE"]

    assert entry["occurrence_count"] == 2
    assert entry["machine_ids"] == ["M001", "M002"]
    assert len(entry["case_ids"]) == 2


def test_tracks_severity():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [
                {"name": "A", "severity": "HIGH"},
                {"name": "B", "severity": "WARNING"},
            ],
        ),
        make_case(
            "M002",
            [{"name": "C", "severity": "HIGH"}],
        ),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["finding_severity_counts"] == {
        "HIGH": 2,
        "WARNING": 1,
    }


def test_missing_severity_becomes_unknown():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "A"}],
        )
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["finding_severity_counts"] == {
        "UNKNOWN": 1,
    }


def test_affected_machine_ids():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "A"}]),
        make_case("M002", []),
        make_case("M003", [{"name": "B"}]),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["affected_machine_ids"] == [
        "M001",
        "M003",
    ]


def test_machine_findings():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [
                {"name": "A", "severity": "HIGH"},
                {"name": "B", "severity": "LOW"},
            ],
        ),
        make_case(
            "M002",
            [{"name": "A", "severity": "HIGH"}],
        ),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert len(result["machine_findings"]["M001"]) == 2
    assert len(result["machine_findings"]["M002"]) == 1
    assert result["machine_findings"]["M001"][0]["finding_key"] == "A"


def test_excludes_cases_outside_fleet():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "A"}]),
        make_case("OUTSIDE", [{"name": "A"}]),
    ]

    result = FleetFindingIntelligence(
        fleet,
        cases,
    ).projection()

    assert result["summary"]["total_finding_occurrences"] == 1
    assert result["affected_machine_ids"] == ["M001"]


def test_projection_is_defensive():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "A", "severity": "HIGH"}],
        )
    ]

    aggregation = FleetFindingIntelligence(
        fleet,
        cases,
    )

    projection = aggregation.projection()
    projection["finding_occurrences"]["A"]["machine_ids"].append(
        "MUTATED"
    )

    fresh = aggregation.projection()

    assert "MUTATED" not in (
        fresh["finding_occurrences"]["A"]["machine_ids"]
    )


def test_does_not_mutate_cases():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [{"name": "A", "severity": "HIGH"}],
    )

    original = list(case.findings)

    FleetFindingIntelligence(
        fleet,
        [case],
    ).projection()

    assert case.findings == original


def test_projection_surface():
    result = FleetFindingIntelligence(
        make_fleet()
    ).projection()

    assert set(result.keys()) == {
        "fleet",
        "summary",
        "affected_machine_ids",
        "finding_severity_counts",
        "finding_occurrences",
        "recurring_findings",
        "machine_findings",
    }


def test_no_diagnostic_or_remediation_lifecycle():
    aggregation = FleetFindingIntelligence(
        make_fleet()
    )

    assert not hasattr(aggregation, "diagnose")
    assert not hasattr(aggregation, "execute")
    assert not hasattr(aggregation, "authorize")
    assert not hasattr(aggregation, "remediate")
    assert not hasattr(aggregation, "verify")
