from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_signal_correlation import FleetSignalCorrelation
from engine.managed_machine import ManagedMachine


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
    fleet.add_machine(
        ManagedMachine(
            machine_id="M003",
            hostname="PC-003",
            platform="Windows",
            operating_system="Windows 11",
        )
    )

    return fleet


def make_case(machine_id, signals):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.signals = list(signals)
    return case


def test_requires_fleet():
    try:
        FleetSignalCorrelation(object())
        assert False
    except ValueError:
        pass


def test_requires_diagnostic_cases():
    fleet = make_fleet()

    try:
        FleetSignalCorrelation(fleet, [object()])
        assert False
    except ValueError:
        pass


def test_empty_projection():
    result = FleetSignalCorrelation(
        make_fleet()
    ).projection()

    assert result["summary"]["unique_signal_count"] == 0
    assert result["summary"]["total_signal_occurrences"] == 0
    assert result["affected_machine_ids"] == []


def test_aggregates_unique_signals():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "HIGH_MEMORY"}]),
        make_case("M002", [{"name": "DISK_WARNING"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert result["summary"]["unique_signal_count"] == 2


def test_recurring_signal_requires_multiple_machines():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "HIGH_MEMORY"}]),
        make_case("M002", [{"name": "HIGH_MEMORY"}]),
        make_case("M003", [{"name": "DISK_WARNING"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert "HIGH_MEMORY" in result["recurring_signals"]
    assert "DISK_WARNING" not in result["recurring_signals"]


def test_fleet_wide_signal():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "NETWORK_FAILURE"}]),
        make_case("M002", [{"name": "NETWORK_FAILURE"}]),
        make_case("M003", [{"name": "NETWORK_FAILURE"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert "NETWORK_FAILURE" in result["fleet_wide_signals"]


def test_signal_occurrence_tracks_machines_and_cases():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "HIGH_MEMORY"}]),
        make_case("M002", [{"name": "HIGH_MEMORY"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    entry = result["signal_occurrences"]["HIGH_MEMORY"]

    assert entry["occurrence_count"] == 2
    assert entry["machine_ids"] == ["M001", "M002"]
    assert len(entry["case_ids"]) == 2


def test_affected_machine_ids():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "HIGH_MEMORY"}]),
        make_case("M002", []),
        make_case("M003", [{"name": "DISK_WARNING"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert result["affected_machine_ids"] == ["M001", "M003"]


def test_machine_signal_counts():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [
                {"name": "A"},
                {"name": "B"},
            ],
        ),
        make_case(
            "M002",
            [{"name": "A"}],
        ),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert result["machine_signal_counts"] == {
        "M001": 2,
        "M002": 1,
    }


def test_summary_counts_total_occurrences():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [
                {"name": "A"},
                {"name": "B"},
            ],
        ),
        make_case(
            "M002",
            [{"name": "A"}],
        ),
    ]

    summary = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()["summary"]

    assert summary["unique_signal_count"] == 2
    assert summary["total_signal_occurrences"] == 3
    assert summary["recurring_signal_count"] == 1
    assert summary["affected_machine_count"] == 2


def test_excludes_cases_outside_fleet():
    fleet = make_fleet()

    cases = [
        make_case("M001", [{"name": "A"}]),
        make_case("OUTSIDE", [{"name": "A"}]),
    ]

    result = FleetSignalCorrelation(
        fleet,
        cases,
    ).projection()

    assert result["summary"]["total_signal_occurrences"] == 1
    assert result["affected_machine_ids"] == ["M001"]


def test_projection_is_defensive():
    fleet = make_fleet()

    cases = [
        make_case(
            "M001",
            [{"name": "HIGH_MEMORY"}],
        )
    ]

    aggregation = FleetSignalCorrelation(
        fleet,
        cases,
    )

    projection = aggregation.projection()
    projection["signal_occurrences"]["HIGH_MEMORY"]["machine_ids"].append(
        "MUTATED"
    )

    fresh = aggregation.projection()

    assert "MUTATED" not in fresh[
        "signal_occurrences"
    ]["HIGH_MEMORY"]["machine_ids"]


def test_does_not_mutate_cases():
    fleet = make_fleet()

    case = make_case(
        "M001",
        [{"name": "HIGH_MEMORY"}],
    )

    original = list(case.signals)

    FleetSignalCorrelation(
        fleet,
        [case],
    ).projection()

    assert case.signals == original


def test_projection_surface():
    fleet = make_fleet()

    result = FleetSignalCorrelation(
        fleet,
    ).projection()

    assert set(result.keys()) == {
        "fleet",
        "summary",
        "affected_machine_ids",
        "machine_signal_counts",
        "signal_occurrences",
        "recurring_signals",
        "fleet_wide_signals",
    }


def test_no_diagnostic_or_remediation_lifecycle():
    aggregation = FleetSignalCorrelation(
        make_fleet()
    )

    assert not hasattr(aggregation, "diagnose")
    assert not hasattr(aggregation, "execute")
    assert not hasattr(aggregation, "authorize")
    assert not hasattr(aggregation, "remediate")
    assert not hasattr(aggregation, "verify")
