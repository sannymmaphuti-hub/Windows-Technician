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
from engine.windows_system_diagnostic import (
    WindowsSystemDiagnostic,
)
from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)


def _healthy_evidence():
    return WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )


def _problem_evidence():
    return WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )


def test_dispatcher_supports_system_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    assert dispatcher.has_domain("SYSTEM")
    assert dispatcher.has_domain(" system ")


def test_system_adapter_is_available():
    adapter = WindowsDiagnosticExecutionAdapter(
        "SYSTEM"
    )

    assert adapter.domain == "SYSTEM"
    assert isinstance(
        adapter.implementation,
        WindowsSystemDiagnostic,
    )


def test_adapter_executes_system_diagnostic():
    adapter = WindowsDiagnosticExecutionAdapter(
        "SYSTEM"
    )

    result = adapter.execute(
        _problem_evidence()
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )
    assert len(result.signals) == 1
    assert len(result.findings) == 1
    assert len(result.recommendations) == 1


def test_dispatcher_executes_system_diagnostic():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "SYSTEM",
        evidence=_problem_evidence(),
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )
    assert result.signals[0].signal_type == (
        "SYSTEM_OS_INFORMATION_MISSING"
    )


def test_system_signal_identity_is_preserved():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "SYSTEM",
        evidence=_problem_evidence(),
    )

    assert result.signals[0] is (
        result.findings[0].supporting_signals[0]
    )


def test_orchestrator_attaches_system_result_to_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )
    case = DiagnosticCase()

    returned_case = orchestrator.investigate(
        case,
        "SYSTEM",
        evidence=_problem_evidence(),
    )

    assert returned_case is case
    assert len(case.signals) == 1
    assert len(case.findings) == 1
    assert len(case.recommendations) == 1

    assert case.signals[0].signal_type == (
        "SYSTEM_OS_INFORMATION_MISSING"
    )


def test_system_diagnostic_creates_no_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )
    case = DiagnosticCase()

    orchestrator.investigate(
        case,
        "SYSTEM",
        evidence=_problem_evidence(),
    )

    assert not hasattr(
        case,
        "remediation_actions",
    ) or case.remediation_actions == []


def test_healthy_system_produces_no_findings():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch(
        "SYSTEM",
        evidence=_healthy_evidence(),
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_explicit_none_is_rejected():
    dispatcher = WindowsDiagnosticDispatcher()

    try:
        dispatcher.dispatch(
            "SYSTEM",
            evidence=None,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Explicit None must be rejected."
        )


def test_omitted_evidence_remains_compatible():
    dispatcher = WindowsDiagnosticDispatcher()

    result = dispatcher.dispatch("SYSTEM")

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )
    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []