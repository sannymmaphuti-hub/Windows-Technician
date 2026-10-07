# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC DOMAIN RESOLUTION TESTS
# ==========================================

from engine.windows_diagnostic_domain_resolution import (
    WindowsDiagnosticDomainResolution,
)


def test_process_domain_resolves_to_implemented_capability():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "PROCESS"
    )

    assert resolution.domain == "PROCESS"
    assert resolution.capability_supported is True
    assert resolution.implemented is True


def test_memory_domain_resolves_to_implemented_capability():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "MEMORY"
    )

    assert resolution.domain == "MEMORY"
    assert resolution.capability_supported is True
    assert resolution.implemented is True


def test_network_domain_resolves_to_implemented_capability():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "NETWORK"
    )

    assert resolution.domain == "NETWORK"
    assert resolution.capability_supported is True
    assert resolution.implemented is True


def test_storage_domain_is_supported_and_implemented():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "STORAGE"
    )

    assert resolution.domain == "STORAGE"
    assert resolution.capability_supported is True
    assert resolution.implemented is True
    assert resolution.investigator is not None
    assert resolution.engine is not None


def test_services_domain_is_supported_and_implemented():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "SERVICES"
    )

    assert resolution.domain == "SERVICES"
    assert resolution.capability_supported is True
    assert resolution.implemented is True
    assert resolution.investigator is not None
    assert resolution.engine is not None


def test_startup_domain_is_supported_and_implemented():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "STARTUP"
    )

    assert resolution.domain == "STARTUP"
    assert resolution.capability_supported is True
    assert resolution.investigator is not None
    assert resolution.engine is not None
    assert resolution.implemented is True

def test_system_domain_is_supported_and_implemented():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "SYSTEM"
    )

    assert resolution.domain == "SYSTEM"
    assert resolution.capability_supported is True
    assert resolution.implemented is True
    assert resolution.investigator is not None
    assert resolution.engine is not None
    
def test_resolution_normalizes_domain():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        " memory "
    )

    assert resolution.domain == "MEMORY"


def test_unknown_domain_is_not_supported():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "UNKNOWN"
    )

    assert resolution is not None
    assert resolution.capability_supported is False
    assert resolution.implemented is False


def test_none_domain_is_not_supported():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        None
    )

    assert resolution is not None
    assert resolution.capability_supported is False
    assert resolution.implemented is False


def test_empty_domain_is_not_supported():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        ""
    )

    assert resolution is not None
    assert resolution.capability_supported is False
    assert resolution.implemented is False


def test_resolution_exposes_investigator_for_implemented_domain():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "NETWORK"
    )

    assert resolution.investigator is not None
    assert resolution.investigator.domain == "NETWORK"


def test_resolution_has_no_investigator_for_unknown_domain():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "UNKNOWN"
    )

    assert resolution.investigator is None


def test_resolution_exposes_engine_for_implemented_domain():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "NETWORK"
    )

    assert resolution.engine is not None


def test_resolution_has_storage_engine():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "STORAGE"
    )

    assert resolution.engine is not None
    assert resolution.implemented is True

def test_resolution_does_not_create_diagnostic_case():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "MEMORY"
    )

    assert not hasattr(resolution, "case")
    assert not hasattr(resolution, "diagnostic_case")


def test_resolution_does_not_authorize_remediation():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "MEMORY"
    )

    assert not hasattr(resolution, "authorized")
    assert not hasattr(resolution, "authorization_status")


def test_resolution_does_not_execute_diagnostics():
    resolution = WindowsDiagnosticDomainResolution.resolve(
        "NETWORK"
    )

    assert not hasattr(resolution, "result")
    assert not hasattr(resolution, "diagnosis")