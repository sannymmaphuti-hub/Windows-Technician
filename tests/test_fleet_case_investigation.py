import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_investigation import FleetCaseInvestigation
from engine.fleet_investigation_target import FleetInvestigationTarget


def make_fleet():
    return Fleet("Test Fleet")


def make_target(machine_id):
    return FleetInvestigationTarget(
        machine_id=machine_id,
        problem_type="MEMORY_PRESSURE",
        domain="MEMORY",
        reason="fleet pattern",
    )


def make_case(machine_id):
    case = DiagnosticCase()
    case.machine_id = machine_id
    return case


def test_investigation_requires_fleet():
    with pytest.raises(ValueError):
        FleetCaseInvestigation(None)


def test_resolve_requires_target_list():
    investigation = FleetCaseInvestigation(make_fleet())

    with pytest.raises(ValueError):
        investigation.resolve_cases(None, [])


def test_resolve_requires_case_list():
    investigation = FleetCaseInvestigation(make_fleet())

    with pytest.raises(ValueError):
        investigation.resolve_cases([], None)


def test_resolve_rejects_invalid_target():
    investigation = FleetCaseInvestigation(make_fleet())

    with pytest.raises(ValueError):
        investigation.resolve_cases(
            [object()],
            [],
        )


def test_resolve_rejects_invalid_case():
    investigation = FleetCaseInvestigation(make_fleet())

    with pytest.raises(ValueError):
        investigation.resolve_cases(
            [],
            [object()],
        )


def test_resolves_existing_case_by_machine_id():
    investigation = FleetCaseInvestigation(make_fleet())

    target = make_target("m1")
    case = make_case("m1")

    resolved = investigation.resolve_cases(
        [target],
        [case],
    )

    assert len(resolved) == 1
    assert resolved[0]["target"] is target
    assert resolved[0]["case"] is case


def test_unresolved_machine_has_no_case():
    investigation = FleetCaseInvestigation(make_fleet())

    target = make_target("m1")
    case = make_case("m2")

    resolved = investigation.resolve_cases(
        [target],
        [case],
    )

    assert resolved[0]["case"] is None


def test_multiple_targets_resolve_independently():
    investigation = FleetCaseInvestigation(make_fleet())

    target_one = make_target("m1")
    target_two = make_target("m2")

    case_one = make_case("m1")
    case_two = make_case("m2")

    resolved = investigation.resolve_cases(
        [target_one, target_two],
        [case_one, case_two],
    )

    assert resolved[0]["case"] is case_one
    assert resolved[1]["case"] is case_two


def test_case_without_machine_id_is_ignored():
    investigation = FleetCaseInvestigation(make_fleet())

    case = DiagnosticCase()

    resolved = investigation.resolve_cases(
        [make_target("m1")],
        [case],
    )

    assert resolved[0]["case"] is None


def test_empty_targets_return_empty_result():
    investigation = FleetCaseInvestigation(make_fleet())

    assert investigation.resolve_cases([], []) == []


def test_resolution_does_not_modify_cases():
    investigation = FleetCaseInvestigation(make_fleet())

    case = make_case("m1")
    original_machine_id = case.machine_id

    investigation.resolve_cases(
        [make_target("m1")],
        [case],
    )

    assert case.machine_id == original_machine_id


def test_resolution_does_not_modify_target():
    investigation = FleetCaseInvestigation(make_fleet())

    target = make_target("m1")

    investigation.resolve_cases(
        [target],
        [make_case("m1")],
    )

    assert target.machine_id == "m1"
    assert target.problem_type == "MEMORY_PRESSURE"


def test_result_does_not_create_new_case():
    investigation = FleetCaseInvestigation(make_fleet())

    case = make_case("m1")

    resolved = investigation.resolve_cases(
        [make_target("m1")],
        [case],
    )

    assert resolved[0]["case"] is case


def test_investigation_does_not_own_remediation():
    investigation = FleetCaseInvestigation(make_fleet())

    assert not hasattr(investigation, "remediation")
    assert not hasattr(investigation, "authorization")


def test_investigation_does_not_create_fleet_case():
    investigation = FleetCaseInvestigation(make_fleet())

    resolved = investigation.resolve_cases(
        [make_target("m1")],
        [make_case("m1")],
    )

    assert not hasattr(resolved[0], "fleet_case")
