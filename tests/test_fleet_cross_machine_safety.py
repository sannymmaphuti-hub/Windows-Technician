import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.fleet import Fleet
from engine.fleet_problem import FleetProblem
from engine.fleet_problem_model import FleetProblemModel
from engine.fleet_pattern_detection import FleetPatternDetection
from engine.managed_machine import ManagedMachine


def make_machine(machine_id):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=machine_id,
        platform="Windows",
        operating_system="Windows 11",
    )


def make_fleet(machine_count=3):
    fleet = Fleet("Isolation Fleet")

    for index in range(1, machine_count + 1):
        fleet.add_machine(make_machine(f"m{index}"))

    return fleet


def make_case(machine_id, finding_type="CPU_PRESSURE"):
    case = DiagnosticCase()
    case.machine_id = machine_id

    case.set_findings(
        [
            Finding(
                finding_type=finding_type,
                category="CPU",
                severity="HIGH",
                description=f"{finding_type} on {machine_id}",
            )
        ]
    )

    return case


def make_problem(
    machine_ids,
    problem_type="CPU_PRESSURE",
    severity="HIGH",
):
    return FleetProblem(
        problem_type=problem_type,
        domain="CPU",
        severity=severity,
        machine_ids=machine_ids,
    )


def test_problem_model_ignores_case_for_machine_outside_fleet():
    fleet = make_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        make_case("m1"),
        make_case("outside-fleet"),
    ]

    problems = model.build(cases)

    assert len(problems) == 1
    assert problems[0].machine_ids == ["m1"]


def test_problem_model_preserves_machine_separation():
    fleet = make_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        make_case("m1", "CPU_PRESSURE"),
        make_case("m2", "MEMORY_PRESSURE"),
    ]

    problems = model.build(cases)

    assert len(problems) == 2

    by_type = {
        problem.problem_type: problem
        for problem in problems
    }

    assert by_type["CPU_PRESSURE"].machine_ids == ["m1"]
    assert by_type["MEMORY_PRESSURE"].machine_ids == ["m2"]


def test_problem_model_does_not_invent_machine_ids():
    fleet = make_fleet()
    model = FleetProblemModel(fleet)

    problems = model.build([make_case("m1")])

    assert problems[0].machine_ids == ["m1"]
    assert "m2" not in problems[0].machine_ids
    assert "m3" not in problems[0].machine_ids


def test_pattern_detection_filters_non_fleet_machine_ids():
    fleet = make_fleet()
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["m1", "outside-fleet"])

    detected = detector.detect([problem])

    assert len(detected) == 1
    assert detected[0].machine_ids == ["m1"]


def test_pattern_detection_does_not_create_empty_pattern():
    fleet = make_fleet()
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["outside-fleet"])

    assert detector.detect([problem]) == []


def test_machine_counts_are_based_on_actual_affected_machines():
    fleet = make_fleet()
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["m1", "m2"])

    detected = detector.detect([problem])

    assert detected[0].affected_machine_count == 2
    assert detected[0].fleet_machine_count == 3
    assert detected[0].affected_machine_ratio == pytest.approx(2 / 3)


def test_isolated_machine_remains_isolated():
    fleet = make_fleet()
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["m1"])

    detected = detector.detect([problem])

    assert detected[0].pattern_type == "ISOLATED"


def test_repeated_machine_pattern_remains_repeated():
    fleet = make_fleet(machine_count=5)
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["m1", "m2"])

    detected = detector.detect([problem])

    assert detected[0].affected_machine_count == 2
    assert detected[0].fleet_machine_count == 5
    assert detected[0].affected_machine_ratio == pytest.approx(2 / 5)
    assert detected[0].pattern_type == "REPEATED"


def test_widespread_pattern_requires_actual_fleet_distribution():
    fleet = make_fleet()
    detector = FleetPatternDetection(fleet)

    problem = make_problem(["m1", "m2", "m3"])

    detected = detector.detect([problem])

    assert detected[0].pattern_type == "WIDESPREAD"
