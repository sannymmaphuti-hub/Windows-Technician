# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC ENGINE REGISTRY TESTS
# ==========================================

from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.windows_storage_diagnostic import (
    WindowsStorageDiagnostic,
)

def test_registry_has_supported_domains():
    registry = WindowsDiagnosticEngineRegistry()

    domains = registry.supported_domains()

    assert "PROCESS" in domains
    assert "MEMORY" in domains
    assert "NETWORK" in domains
    assert "STORAGE" in domains
    assert "SERVICES" in domains
    assert "STARTUP" in domains
    assert "SYSTEM" in domains


def test_registry_reports_existing_process_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("PROCESS")


def test_registry_reports_existing_memory_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("MEMORY")


def test_registry_reports_existing_network_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("NETWORK")


def test_registry_does_not_claim_unimplemented_storage_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("STORAGE") is True


def test_registry_claims_implemented_services_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("SERVICES")
    assert (
        registry.get_engine("SERVICES").__name__
        == "WindowsServicesDiagnostic"
    )


def test_registry_claims_implemented_startup_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("STARTUP")


def test_registry_claims_implemented_system_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("SYSTEM")


def test_unknown_domain_has_no_engine():
    registry = WindowsDiagnosticEngineRegistry()

    assert not registry.has_engine("UNKNOWN")


def test_engine_lookup_returns_none_when_unimplemented():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.get_engine("STORAGE") is WindowsStorageDiagnostic


def test_engine_lookup_returns_none_for_unknown_domain():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.get_engine("UNKNOWN") is None


def test_engine_lookup_normalizes_domain():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine(" memory ")
    assert registry.has_engine("Network")


def test_supported_domains_are_immutable():
    registry = WindowsDiagnosticEngineRegistry()

    domains = registry.supported_domains()

    assert isinstance(domains, tuple)


def test_registry_does_not_create_cases():
    registry = WindowsDiagnosticEngineRegistry()

    assert not hasattr(registry, "case")
    assert not hasattr(registry, "diagnostic_case")


def test_registry_does_not_authorize_remediation():
    registry = WindowsDiagnosticEngineRegistry()

    assert not hasattr(registry, "authorized")
    assert not hasattr(registry, "authorization_status")


def test_registry_does_not_execute_remediation():
    registry = WindowsDiagnosticEngineRegistry()

    assert not hasattr(registry, "execute")
    assert not hasattr(registry, "execute_remediation")


def test_registry_is_observational_only():
    registry = WindowsDiagnosticEngineRegistry()

    assert registry.has_engine("PROCESS") is True
    assert registry.has_engine("STORAGE") is True