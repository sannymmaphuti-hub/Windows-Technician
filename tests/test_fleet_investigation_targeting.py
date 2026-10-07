import pytest

from engine.fleet import Fleet
from engine.fleet_investigation_target import FleetInvestigationTarget
from engine.fleet_investigation_targeting import FleetInvestigationTargeting
from engine.fleet_problem_pattern import FleetProblemPattern
from engine.managed_machine import ManagedMachine


def make_machine(machine_id):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_fleet(*machine_ids):
    fleet = Fleet("Test Fleet")

    for machine_id in machine_ids:
        fleet.add_machine(make_machine(machine_id))

    return fleet


def make_pattern(machine_ids):
    return FleetProblemPattern(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        machine_ids=machine_ids,
        fleet_machine_count=10,
    )


def test_target_requires_machine_id():
    with pytest.raises(ValueError):
        FleetInvestigationTarget(
            None,
            "MEMORY_PRESSURE",
            "MEMORY",
            "reason",
        )


def test_target_requires_problem_type():
    with pytest.raises(ValueError):
        FleetInvestigationTarget(
            "m1",
            "",
            "MEMORY",
            "reason",
        )


def test_target_requires_domain():
    with pytest.raises(ValueError):
        FleetInvestigationTarget(
            "m1",
            "MEMORY_PRESSURE",
            "",
            "reason",
        )


def test_target_requires_reason():
    with pytest.raises(ValueError):
        FleetInvestigationTarget(
            "m1",
            "MEMORY_PRESSURE",
            "MEMORY",
            "",
        )


def test_target_evidence_contains_complete_context():
    target = FleetInvestigationTarget(
        "m1",
        "MEMORY_PRESSURE",
        "MEMORY",
        "fleet pattern",
    )

    assert target.to_evidence() == {
        "machine_id": "m1",
        "problem_type": "MEMORY_PRESSURE",
        "domain": "MEMORY",
        "reason": "fleet pattern",
    }


def test_targeting_selects_pattern_machines():
    fleet = make_fleet("m1", "m2", "m3")

    targets = FleetInvestigationTargeting(fleet).select(
        make_pattern(["m1", "m2"])
    )

    assert [target.machine_id for target in targets] == [
        "m1",
        "m2",
    ]


def test_targeting_preserves_problem_context():
    fleet = make_fleet("m1", "m2")

    targets = FleetInvestigationTargeting(fleet).select(
        make_pattern(["m1"])
    )

    assert targets[0].problem_type == "MEMORY_PRESSURE"
    assert targets[0].domain == "MEMORY"


def test_targeting_ignores_machine_outside_fleet():
    fleet = make_fleet("m1", "m2")

    targets = FleetInvestigationTargeting(fleet).select(
        make_pattern(["m1", "outside"])
    )

    assert [target.machine_id for target in targets] == ["m1"]


def test_targeting_returns_empty_when_no_pattern_machine_is_in_fleet():
    fleet = make_fleet("m1", "m2")

    targets = FleetInvestigationTargeting(fleet).select(
        make_pattern(["outside"])
    )

    assert targets == []


def test_targeting_rejects_invalid_pattern():
    fleet = make_fleet("m1")

    with pytest.raises(ValueError):
        FleetInvestigationTargeting(fleet).select(None)


def test_targeting_requires_fleet():
    with pytest.raises(ValueError):
        FleetInvestigationTargeting(None)


def test_targeting_does_not_modify_fleet():
    fleet = make_fleet("m1", "m2")
    original_ids = fleet.machine_ids

    FleetInvestigationTargeting(fleet).select(
        make_pattern(["m1"])
    )

    assert fleet.machine_ids == original_ids


def test_target_does_not_own_case_lifecycle():
    target = FleetInvestigationTarget(
        "m1",
        "MEMORY_PRESSURE",
        "MEMORY",
        "fleet pattern",
    )

    assert not hasattr(target, "case")
    assert not hasattr(target, "workflow")


def test_target_does_not_authorize_or_remediate():
    target = FleetInvestigationTarget(
        "m1",
        "MEMORY_PRESSURE",
        "MEMORY",
        "fleet pattern",
    )

    assert not hasattr(target, "authorization")
    assert not hasattr(target, "remediation")
    assert not hasattr(target, "recovery")


def test_targeting_creates_independent_target_objects():
    fleet = make_fleet("m1", "m2")

    targets = FleetInvestigationTargeting(fleet).select(
        make_pattern(["m1", "m2"])
    )

    assert targets[0] is not targets[1]
