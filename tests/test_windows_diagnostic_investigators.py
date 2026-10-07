# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATORS TESTS
# ==========================================

import pytest

from engine.windows_diagnostic_investigator import (
    WindowsDiagnosticInvestigator,
)


def test_supported_investigators_exist():
    investigators = WindowsDiagnosticInvestigator.supported()

    assert "PROCESS" in investigators
    assert "MEMORY" in investigators
    assert "NETWORK" in investigators
    assert "STORAGE" in investigators
    assert "SERVICES" in investigators
    assert "STARTUP" in investigators
    assert "SYSTEM" in investigators


def test_supported_investigators_are_unique():
    investigators = WindowsDiagnosticInvestigator.supported()

    assert len(investigators) == len(set(investigators))


@pytest.mark.parametrize(
    "domain",
    [
        "PROCESS",
        "MEMORY",
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    ],
)
def test_supported_domain_has_investigator(domain):
    investigator = WindowsDiagnosticInvestigator.for_domain(
        domain
    )

    assert investigator is not None
    assert investigator.domain == domain


def test_investigator_domain_is_normalized():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        " memory "
    )

    assert investigator.domain == "MEMORY"


def test_unknown_domain_has_no_investigator():
    assert (
        WindowsDiagnosticInvestigator.for_domain("UNKNOWN")
        is None
    )


def test_empty_domain_has_no_investigator():
    assert (
        WindowsDiagnosticInvestigator.for_domain("")
        is None
    )


def test_none_domain_has_no_investigator():
    assert (
        WindowsDiagnosticInvestigator.for_domain(None)
        is None
    )


def test_investigator_is_not_a_diagnostic_case():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "NETWORK"
    )

    assert not hasattr(investigator, "case_id")
    assert not hasattr(investigator, "lifecycle_state")


def test_investigator_does_not_authorize_remediation():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "MEMORY"
    )

    assert not hasattr(investigator, "authorized")
    assert not hasattr(
        investigator,
        "authorization_status",
    )


def test_investigator_does_not_execute_remediation():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "STORAGE"
    )

    assert not hasattr(investigator, "execute")
    assert not hasattr(
        investigator,
        "execute_remediation",
    )


def test_investigator_does_not_own_workflow():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "SERVICES"
    )

    assert not hasattr(investigator, "workflow")
    assert not hasattr(investigator, "workflow_id")


def test_each_domain_returns_an_independent_investigator():
    first = WindowsDiagnosticInvestigator.for_domain(
        "MEMORY"
    )

    second = WindowsDiagnosticInvestigator.for_domain(
        "MEMORY"
    )

    assert first is not second
    assert first.domain == second.domain


def test_investigator_exposes_domain_only_as_identity():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "SYSTEM"
    )

    assert investigator.domain == "SYSTEM"


def test_investigator_does_not_execute_diagnostics_on_creation():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "PROCESS"
    )

    assert not hasattr(investigator, "result")
    assert not hasattr(investigator, "findings")
    assert not hasattr(investigator, "observations")


def test_registry_is_not_mutated_by_returned_investigator():
    investigators = WindowsDiagnosticInvestigator.supported()

    investigator = WindowsDiagnosticInvestigator.for_domain(
        "NETWORK"
    )

    assert "NETWORK" in investigators
    assert investigator.domain == "NETWORK"


def test_unsupported_domain_does_not_create_specialized_type():
    investigator = WindowsDiagnosticInvestigator.for_domain(
        "UNKNOWN"
    )

    assert investigator is None