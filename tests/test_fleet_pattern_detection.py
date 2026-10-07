import pytest

from engine.fleet import Fleet
from engine.fleet_problem import FleetProblem
from engine.fleet_problem_pattern import FleetProblemPattern
from engine.fleet_pattern_detection import FleetPatternDetection
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


def make_problem(problem_type, domain, machine_ids, severity="MEDIUM"):
    return FleetProblem(
        problem_type=problem_type,
        domain=domain,
        severity=severity,
        machine_ids=machine_ids,
    )


def test_pattern_requires_problem_type():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type=None,
            domain="MEMORY",
            machine_ids=["m1"],
            fleet_machine_count=1,
        )


def test_pattern_requires_domain():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type="MEMORY_PRESSURE",
            domain=None,
            machine_ids=["m1"],
            fleet_machine_count=1,
        )


def test_single_machine_problem_is_isolated():
    pattern = FleetProblemPattern(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        machine_ids=["m1"],
        fleet_machine_count=10,
    )

    assert pattern.affected_machine_count == 1
    assert pattern.affected_machine_ratio == 0.1
    assert pattern.pattern_type == "ISOLATED"


def test_multi_machine_problem_below_half_is_repeated():
    pattern = FleetProblemPattern(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        machine_ids=["m1", "m2", "m3"],
        fleet_machine_count=10,
    )

    assert pattern.affected_machine_count == 3
    assert pattern.affected_machine_ratio == 0.3
    assert pattern.pattern_type == "REPEATED"


def test_half_of_fleet_is_widespread():
    pattern = FleetProblemPattern(
        problem_type="NETWORK_FAILURE",
        domain="NETWORK",
        machine_ids=["m1", "m2", "m3", "m4", "m5"],
        fleet_machine_count=10,
    )

    assert pattern.affected_machine_ratio == 0.5
    assert pattern.pattern_type == "WIDESPREAD"


def test_all_fleet_machines_are_widespread():
    pattern = FleetProblemPattern(
        problem_type="SERVICE_STOPPED",
        domain="SERVICES",
        machine_ids=["m1", "m2", "m3"],
        fleet_machine_count=3,
    )

    assert pattern.affected_machine_ratio == 1.0
    assert pattern.pattern_type == "WIDESPREAD"


def test_duplicate_machine_ids_are_removed():
    pattern = FleetProblemPattern(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        machine_ids=["m1", "m1", "m2"],
        fleet_machine_count=3,
    )

    assert pattern.machine_ids == ["m1", "m2"]
    assert pattern.affected_machine_count == 2


def test_machine_count_cannot_exceed_fleet():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type="MEMORY_PRESSURE",
            domain="MEMORY",
            machine_ids=["m1", "m2", "m3"],
            fleet_machine_count=2,
        )


def test_negative_fleet_count_rejected():
    with pytest.raises(ValueError):
        FleetProblemPattern(
            problem_type="MEMORY_PRESSURE",
            domain="MEMORY",
            machine_ids=[],
            fleet_machine_count=-1,
        )


def test_empty_fleet_ratio_is_zero():
    pattern = FleetProblemPattern(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        machine_ids=[],
        fleet_machine_count=0,
    )

    assert pattern.affected_machine_ratio == 0.0
    assert pattern.pattern_type == "ISOLATED"


def test_detection_creates_pattern_from_fleet_problem():
    fleet = make_fleet("m1", "m2", "m3", "m4")

    problem = make_problem(
        "MEMORY_PRESSURE",
        "MEMORY",
        ["m1", "m2"],
    )

    patterns = FleetPatternDetection(fleet).detect([problem])

    assert len(patterns) == 1
    assert patterns[0].problem_type == "MEMORY_PRESSURE"
    assert patterns[0].domain == "MEMORY"
    assert patterns[0].machine_ids == ["m1", "m2"]
    assert patterns[0].pattern_type == "WIDESPREAD"


def test_detection_preserves_multiple_problem_patterns():
    fleet = make_fleet("m1", "m2", "m3", "m4", "m5")

    problems = [
        make_problem(
            "MEMORY_PRESSURE",
            "MEMORY",
            ["m1"],
        ),
        make_problem(
            "NETWORK_FAILURE",
            "NETWORK",
            ["m2", "m3"],
        ),
    ]

    patterns = FleetPatternDetection(fleet).detect(problems)

    assert len(patterns) == 2
    assert patterns[0].problem_type == "MEMORY_PRESSURE"
    assert patterns[0].pattern_type == "ISOLATED"
    assert patterns[1].problem_type == "NETWORK_FAILURE"
    assert patterns[1].pattern_type == "REPEATED"


def test_out_of_fleet_machine_ids_are_ignored():
    fleet = make_fleet("m1", "m2")

    problem = make_problem(
        "MEMORY_PRESSURE",
        "MEMORY",
        ["m1", "outside"],
    )

    patterns = FleetPatternDetection(fleet).detect([problem])

    assert len(patterns) == 1
    assert patterns[0].machine_ids == ["m1"]
    assert patterns[0].affected_machine_count == 1


def test_problem_with_no_fleet_members_is_ignored():
    fleet = make_fleet("m1", "m2")

    problem = make_problem(
        "MEMORY_PRESSURE",
        "MEMORY",
        ["outside"],
    )

    patterns = FleetPatternDetection(fleet).detect([problem])

    assert patterns == []


def test_detection_requires_list():
    fleet = make_fleet("m1")

    with pytest.raises(ValueError):
        FleetPatternDetection(fleet).detect(None)


def test_detection_rejects_non_fleet_problem():
    fleet = make_fleet("m1")

    with pytest.raises(ValueError):
        FleetPatternDetection(fleet).detect(["not-a-problem"])


def test_pattern_evidence_contains_complete_distribution():
    pattern = FleetProblemPattern(
        problem_type="CPU_RESOURCE_DEMAND",
        domain="CPU",
        machine_ids=["m1", "m2"],
        fleet_machine_count=4,
    )

    evidence = pattern.to_evidence()

    assert evidence == {
        "problem_type": "CPU_RESOURCE_DEMAND",
        "domain": "CPU",
        "machine_ids": ["m1", "m2"],
        "affected_machine_count": 2,
        "fleet_machine_count": 4,
        "affected_machine_ratio": 0.5,
        "pattern_type": "WIDESPREAD",
        "scope": "WIDESPREAD",
    }


def test_detection_does_not_modify_fleet():
    fleet = make_fleet("m1", "m2")
    original_ids = fleet.machine_ids

    problem = make_problem(
        "MEMORY_PRESSURE",
        "MEMORY",
        ["m1"],
    )

    FleetPatternDetection(fleet).detect([problem])

    assert fleet.machine_ids == original_ids


def test_detection_has_no_authorization_or_remediation_state():
    fleet = make_fleet("m1")

    problem = make_problem(
        "MEMORY_PRESSURE",
        "MEMORY",
        ["m1"],
    )

    patterns = FleetPatternDetection(fleet).detect([problem])

    assert not hasattr(patterns[0], "authorization")
    assert not hasattr(patterns[0], "remediation")
    assert not hasattr(patterns[0], "recovery")
