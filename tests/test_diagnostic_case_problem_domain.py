# ==========================================
# Windows Technician v0.9
# DIAGNOSTIC CASE PROBLEM DOMAIN TESTS
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase


def test_new_case_has_no_problem_domain():
    case = DiagnosticCase()

    assert case.problem_domain is None


def test_case_can_set_problem_domain():
    case = DiagnosticCase()

    case.set_problem_domain("MEMORY")

    assert case.problem_domain == "MEMORY"


def test_case_normalizes_problem_domain():
    case = DiagnosticCase()

    case.set_problem_domain(" network ")

    assert case.problem_domain == "NETWORK"


def test_case_accepts_expanded_windows_domains():
    domains = [
        "PROCESS",
        "MEMORY",
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    ]

    for domain in domains:
        case = DiagnosticCase()

        case.set_problem_domain(domain)

        assert case.problem_domain == domain


def test_case_rejects_unknown_problem_domain():
    case = DiagnosticCase()

    with pytest.raises(ValueError):
        case.set_problem_domain("UNKNOWN")


def test_case_rejects_empty_problem_domain():
    case = DiagnosticCase()

    with pytest.raises(ValueError):
        case.set_problem_domain("")


def test_case_rejects_none_problem_domain():
    case = DiagnosticCase()

    with pytest.raises(ValueError):
        case.set_problem_domain(None)


def test_problem_domain_does_not_create_specialized_case_type():
    case = DiagnosticCase()

    case.set_problem_domain("STORAGE")

    assert isinstance(case, DiagnosticCase)
    assert not hasattr(case, "storage_diagnostic")


def test_problem_domain_does_not_replace_existing_case_identity():
    case = DiagnosticCase()
    original_case_id = case.case_id

    case.set_problem_domain("SERVICES")

    assert case.case_id == original_case_id


def test_problem_domain_does_not_change_case_lifecycle():
    case = DiagnosticCase()

    original_state = case.lifecycle_state

    case.set_problem_domain("STARTUP")

    assert case.lifecycle_state == original_state


def test_problem_domain_does_not_authorize_remediation():
    case = DiagnosticCase()

    case.set_problem_domain("SYSTEM")

    assert not hasattr(case, "authorized")
    assert not hasattr(case, "authorization_status")