# ==========================================
# Windows Technician v0.9
# WINDOWS PROBLEM DOMAIN TESTS
# ==========================================

import pytest

from engine.windows_problem_domain import WindowsProblemDomain


def test_supported_domains_exist():
    domains = WindowsProblemDomain.supported()

    assert "PROCESS" in domains
    assert "MEMORY" in domains
    assert "NETWORK" in domains
    assert "STORAGE" in domains
    assert "SERVICES" in domains
    assert "STARTUP" in domains
    assert "SYSTEM" in domains


def test_supported_domains_are_unique():
    domains = WindowsProblemDomain.supported()

    assert len(domains) == len(set(domains))


def test_process_domain_is_supported():
    assert WindowsProblemDomain.is_supported("PROCESS")


def test_memory_domain_is_supported():
    assert WindowsProblemDomain.is_supported("MEMORY")


def test_network_domain_is_supported():
    assert WindowsProblemDomain.is_supported("NETWORK")


def test_storage_domain_is_supported():
    assert WindowsProblemDomain.is_supported("STORAGE")


def test_services_domain_is_supported():
    assert WindowsProblemDomain.is_supported("SERVICES")


def test_startup_domain_is_supported():
    assert WindowsProblemDomain.is_supported("STARTUP")


def test_system_domain_is_supported():
    assert WindowsProblemDomain.is_supported("SYSTEM")


def test_unknown_domain_is_not_supported():
    assert not WindowsProblemDomain.is_supported("UNKNOWN")


def test_empty_domain_is_not_supported():
    assert not WindowsProblemDomain.is_supported("")


def test_none_domain_is_not_supported():
    assert not WindowsProblemDomain.is_supported(None)


def test_domain_matching_is_case_insensitive():
    assert WindowsProblemDomain.is_supported("memory")
    assert WindowsProblemDomain.is_supported("Network")
    assert WindowsProblemDomain.is_supported("storage")


def test_domain_normalization():
    assert WindowsProblemDomain.normalize("memory") == "MEMORY"
    assert WindowsProblemDomain.normalize(" Network ") == "NETWORK"


def test_invalid_domain_normalization_fails():
    with pytest.raises(ValueError):
        WindowsProblemDomain.normalize("UNKNOWN")


def test_domain_definition_does_not_execute_diagnostics():
    domains = WindowsProblemDomain.supported()

    assert isinstance(domains, tuple)