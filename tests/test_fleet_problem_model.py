# ==========================================
# Windows Technician v0.9
# FLEET PROBLEM MODEL TESTS
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.fleet import Fleet
from engine.fleet_problem import FleetProblem
from engine.fleet_problem_model import FleetProblemModel
from engine.managed_machine import ManagedMachine


def create_machine(
    machine_id,
    hostname,
):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="AMD64",
        operating_system="Windows 11",
    )


def create_case(
    machine_id,
    finding_type="CPU_PRESSURE",
    category="CPU",
    severity="HIGH",
):
    case = DiagnosticCase()
    case.machine_id = machine_id

    case.set_findings(
        [
            Finding(
                finding_type=finding_type,
                category=category,
                severity=severity,
                description=f"{finding_type} detected.",
                supporting_signals=[],
            )
        ]
    )

    return case


def create_fleet():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
        )
    )

    fleet.add_machine(
        create_machine(
            "machine-002",
            "PC-002",
        )
    )

    fleet.add_machine(
        create_machine(
            "machine-003",
            "PC-003",
        )
    )

    return fleet


def test_fleet_problem_requires_a_problem_type():
    with pytest.raises(ValueError):
        FleetProblem(
            problem_type=None,
            domain="CPU",
            severity="HIGH",
            machine_ids=["machine-001"],
        )


def test_fleet_problem_requires_valid_severity():
    with pytest.raises(ValueError):
        FleetProblem(
            problem_type="CPU_PRESSURE",
            domain="CPU",
            severity="UNKNOWN",
            machine_ids=["machine-001"],
        )


def test_single_machine_problem_is_isolated():
    problem = FleetProblem(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        severity="HIGH",
        machine_ids=["machine-001"],
    )

    assert problem.affected_machine_count == 1
    assert problem.scope == "ISOLATED"


def test_multi_machine_problem_is_identified():
    problem = FleetProblem(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        severity="HIGH",
        machine_ids=[
            "machine-001",
            "machine-002",
        ],
    )

    assert problem.affected_machine_count == 2
    assert problem.scope == "MULTI_MACHINE"


def test_duplicate_machine_ids_are_removed():
    problem = FleetProblem(
        problem_type="CPU_PRESSURE",
        domain="CPU",
        severity="HIGH",
        machine_ids=[
            "machine-001",
            "machine-001",
        ],
    )

    assert problem.machine_ids == [
        "machine-001"
    ]


def test_fleet_problem_model_aggregates_same_finding():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        create_case("machine-001"),
        create_case("machine-002"),
    ]

    problems = model.build(cases)

    assert len(problems) == 1

    problem = problems[0]

    assert problem.problem_type == "CPU_PRESSURE"
    assert problem.domain == "CPU"
    assert problem.severity == "HIGH"
    assert problem.machine_ids == [
        "machine-001",
        "machine-002",
    ]
    assert problem.scope == "MULTI_MACHINE"


def test_different_findings_remain_separate():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        create_case(
            "machine-001",
            "CPU_PRESSURE",
            "CPU",
            "HIGH",
        ),
        create_case(
            "machine-002",
            "MEMORY_PRESSURE",
            "MEMORY",
            "HIGH",
        ),
    ]

    problems = model.build(cases)

    assert len(problems) == 2

    problem_types = {
        problem.problem_type
        for problem in problems
    }

    assert problem_types == {
        "CPU_PRESSURE",
        "MEMORY_PRESSURE",
    }


def test_same_problem_keeps_highest_severity():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        create_case(
            "machine-001",
            severity="MEDIUM",
        ),
        create_case(
            "machine-002",
            severity="HIGH",
        ),
    ]

    problems = model.build(cases)

    assert len(problems) == 1
    assert problems[0].severity == "HIGH"


def test_case_from_outside_fleet_is_ignored():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    cases = [
        create_case("outside-machine"),
    ]

    problems = model.build(cases)

    assert problems == []


def test_case_without_machine_identity_is_ignored():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    case = DiagnosticCase()

    problems = model.build([case])

    assert problems == []


def test_malformed_finding_is_ignored():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    case = DiagnosticCase()
    case.machine_id = "machine-001"
    case.findings = [object()]

    problems = model.build([case])

    assert problems == []


def test_fleet_problem_model_does_not_store_cases():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    case = create_case("machine-001")

    model.build([case])

    assert not hasattr(model, "cases")


def test_fleet_problem_model_does_not_modify_cases():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    case = create_case("machine-001")
    original_findings = list(case.findings)

    model.build([case])

    assert case.findings == original_findings


def test_fleet_problem_model_does_not_modify_machines():
    fleet = create_fleet()

    machine = fleet.get_machine("machine-001")
    machine.connection_state = "CONNECTED"
    machine.health_state = "WARNING"

    model = FleetProblemModel(fleet)

    model.build([
        create_case("machine-001")
    ])

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "WARNING"


def test_fleet_problem_model_does_not_create_authorization():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    model.build([
        create_case("machine-001")
    ])

    assert not hasattr(
        model,
        "authorization_status",
    )

    assert not hasattr(
        model,
        "authorized",
    )


def test_fleet_problem_model_does_not_create_remediation():
    fleet = create_fleet()
    model = FleetProblemModel(fleet)

    problems = model.build([
        create_case("machine-001")
    ])

    assert len(problems) == 1

    assert not hasattr(
        problems[0],
        "remediation",
    )

    assert not hasattr(
        problems[0],
        "authorized",
    )


def test_fleet_problem_to_evidence_is_complete():
    problem = FleetProblem(
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        severity="HIGH",
        machine_ids=[
            "machine-001",
            "machine-002",
        ],
    )

    evidence = problem.to_evidence()

    assert evidence == {
        "problem_type": "MEMORY_PRESSURE",
        "domain": "MEMORY",
        "severity": "HIGH",
        "machine_ids": [
            "machine-001",
            "machine-002",
        ],
        "affected_machine_count": 2,
        "scope": "MULTI_MACHINE",
    }