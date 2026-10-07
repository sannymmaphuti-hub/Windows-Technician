# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC CAPABILITIES TESTS
# ==========================================

import pytest

from engine.windows_diagnostic_capability import (
    WindowsDiagnosticCapability,
)


def test_supported_capabilities_exist():
    capabilities = WindowsDiagnosticCapability.supported()

    assert "PROCESS" in capabilities
    assert "MEMORY" in capabilities
    assert "NETWORK" in capabilities
    assert "STORAGE" in capabilities
    assert "SERVICES" in capabilities
    assert "STARTUP" in capabilities
    assert "SYSTEM" in capabilities


def test_supported_capabilities_are_unique():
    capabilities = WindowsDiagnosticCapability.supported()

    assert len(capabilities) == len(set(capabilities))


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
def test_supported_domain_has_diagnostic_capability(domain):
    assert WindowsDiagnosticCapability.is_supported(domain)


def test_unknown_domain_has_no_diagnostic_capability():
    assert not WindowsDiagnosticCapability.is_supported(
        "UNKNOWN"
    )


def test_empty_domain_has_no_diagnostic_capability():
    assert not WindowsDiagnosticCapability.is_supported("")


def test_none_domain_has_no_diagnostic_capability():
    assert not WindowsDiagnosticCapability.is_supported(None)


def test_capability_matching_is_case_insensitive():
    assert WindowsDiagnosticCapability.is_supported(
        "memory"
    )

    assert WindowsDiagnosticCapability.is_supported(
        "Network"
    )

    assert WindowsDiagnosticCapability.is_supported(
        " storage "
    )


def test_capability_normalization():
    assert (
        WindowsDiagnosticCapability.normalize("memory")
        == "MEMORY"
    )

    assert (
        WindowsDiagnosticCapability.normalize(" Network ")
        == "NETWORK"
    )


def test_invalid_capability_normalization_fails():
    with pytest.raises(ValueError):
        WindowsDiagnosticCapability.normalize(
            "UNKNOWN"
        )


def test_capability_registry_returns_immutable_definition():
    capabilities = WindowsDiagnosticCapability.supported()

    assert isinstance(capabilities, tuple)


def test_capability_registry_does_not_execute_diagnostics():
    capabilities = WindowsDiagnosticCapability.supported()

    assert isinstance(capabilities, tuple)


def test_capability_registry_does_not_create_diagnostic_cases():
    capability = WindowsDiagnosticCapability()

    assert not hasattr(capability, "case")
    assert not hasattr(capability, "diagnostic_case")


def test_capability_registry_does_not_authorize_remediation():
    capability = WindowsDiagnosticCapability()

    assert not hasattr(capability, "authorized")
    assert not hasattr(capability, "authorization_status")


def test_capability_registry_does_not_execute_remediation():
    capability = WindowsDiagnosticCapability()

    assert not hasattr(capability, "execute")
    assert not hasattr(capability, "execute_remediation")