# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE DIAGNOSTIC INTEGRATION TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)
from engine.windows_diagnostic_execution_adapter import (
    WindowsDiagnosticExecutionAdapter,
)
from engine.windows_diagnostic_investigation_orchestrator import (
    WindowsDiagnosticInvestigationOrchestrator,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_storage_diagnostic import (
    WindowsStorageDiagnostic,
)


def test_storage_is_registered_as_implemented():
    dispatcher = WindowsDiagnosticDispatcher()

    assert dispatcher.has_domain("STORAGE")


def test_storage_dispatcher_returns_canonical_result():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "STORAGE"
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_dispatcher_is_case_insensitive():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "storage"
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_dispatcher_normalizes_whitespace():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "  STORAGE  "
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_execution_adapter_can_be_created():
    adapter = WindowsDiagnosticExecutionAdapter(
        "STORAGE"
    )

    assert adapter.domain == "STORAGE"


def test_storage_execution_adapter_uses_storage_diagnostic():
    adapter = WindowsDiagnosticExecutionAdapter(
        "STORAGE"
    )

    assert isinstance(
        adapter.implementation,
        WindowsStorageDiagnostic,
    )


def test_storage_execution_adapter_executes_analyze():
    adapter = WindowsDiagnosticExecutionAdapter(
        "STORAGE"
    )

    result = adapter.execute()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_dispatch_does_not_require_evidence():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "STORAGE"
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_can_be_investigated_into_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="STORAGE",
    )

    assert result is case


def test_storage_investigation_populates_canonical_fields():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="STORAGE",
    )

    assert isinstance(
        case.observations,
        list,
    )

    assert isinstance(
        case.signals,
        list,
    )

    assert isinstance(
        case.findings,
        list,
    )

    assert isinstance(
        case.correlations,
        list,
    )

    assert isinstance(
        case.root_cause_candidates,
        list,
    )

    assert isinstance(
        case.recommendations,
        list,
    )


def test_storage_investigation_preserves_case_identity():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()
    case_id = case.case_id

    orchestrator.investigate(
        case=case,
        domain="STORAGE",
    )

    assert case.case_id == case_id


def test_storage_investigation_preserves_case_lifecycle():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()
    lifecycle = case.lifecycle_state

    orchestrator.investigate(
        case=case,
        domain="STORAGE",
    )

    assert case.lifecycle_state == lifecycle


def test_storage_does_not_authorize_remediation():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "authorize",
    )


def test_storage_does_not_execute_remediation():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "remediate",
    )


def test_storage_does_not_create_case():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "create_case",
    )


def test_storage_result_is_fresh_per_execution():
    dispatcher = WindowsDiagnosticDispatcher()

    first = dispatcher.dispatch(
        "STORAGE"
    )

    second = dispatcher.dispatch(
        "STORAGE"
    )

    assert first is not second


def test_storage_result_collections_are_independent():
    dispatcher = WindowsDiagnosticDispatcher()

    first = dispatcher.dispatch(
        "STORAGE"
    )

    second = dispatcher.dispatch(
        "STORAGE"
    )

    first.observations.append(
        "test"
    )

    assert second.observations == []


def test_storage_does_not_require_authorization():
    adapter = WindowsDiagnosticExecutionAdapter(
        "STORAGE"
    )

    assert callable(
        adapter.execute
    )


def test_storage_isolated_from_other_domains():
    dispatcher = WindowsDiagnosticDispatcher()

    assert dispatcher.has_domain("PROCESS")
    assert dispatcher.has_domain("MEMORY")
    assert dispatcher.has_domain("NETWORK")
    assert dispatcher.has_domain("STORAGE")

    assert dispatcher.get_adapter(
        "STORAGE"
    ) is not dispatcher.get_adapter(
        "NETWORK"
    )