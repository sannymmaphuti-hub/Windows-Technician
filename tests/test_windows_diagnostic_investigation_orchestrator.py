# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATION
# ORCHESTRATOR TESTS
# ==========================================


from unittest.mock import Mock

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_investigation_orchestrator import (
    WindowsDiagnosticInvestigationOrchestrator,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)

def test_orchestrator_can_be_created():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert orchestrator is not None


def test_orchestrator_requires_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    with pytest.raises(ValueError):
        orchestrator.investigate(
            case=None,
            domain="NETWORK",
            evidence={},
        )


def test_orchestrator_requires_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    with pytest.raises(ValueError):
        orchestrator.investigate(
            case=case,
            domain=None,
            evidence={},
        )


def test_orchestrator_requires_supported_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    with pytest.raises(ValueError):
        orchestrator.investigate(
            case=case,
            domain="UNKNOWN",
            evidence={},
        )


def test_orchestrator_dispatches_diagnostic():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    diagnostic_result = {
        "findings": [
            {
                "category": "NETWORK",
                "severity": "WARNING",
            }
        ]
    }

    dispatcher.dispatch.return_value = (
        diagnostic_result
    )

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={
            "network": {
                "connected": False
            }
        },
    )

    dispatcher.dispatch.assert_called_once_with(
        "NETWORK",
        evidence={
            "network": {
                "connected": False
            }
        },
    )

    assert result is case


def test_orchestrator_attaches_diagnostic_result_to_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "observations": [
            {
                "category": "NETWORK",
            }
        ],
        "signals": [
            {
                "name": "NETWORK_DISCONNECTED",
            }
        ],
        "findings": [
            {
                "severity": "WARNING",
            }
        ],
        "correlations": [],
        "candidates": [],
        "primary_cause": None,
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert case.observations == [
        {
            "category": "NETWORK",
        }
    ]

    assert case.signals == [
        {
            "name": "NETWORK_DISCONNECTED",
        }
    ]

    assert case.findings == [
        {
            "severity": "WARNING",
        }
    ]


def test_orchestrator_returns_same_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    returned_case = orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert returned_case is case


def test_orchestrator_preserves_case_identity():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()
    case_id = case.case_id

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert case.case_id == case_id


def test_orchestrator_does_not_create_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "case",
    )

    assert not hasattr(
        orchestrator,
        "diagnostic_case",
    )


def test_orchestrator_does_not_authorize_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "authorized",
    )

    assert not hasattr(
        orchestrator,
        "authorization_status",
    )


def test_orchestrator_does_not_execute_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "execute_remediation",
    )

    assert not hasattr(
        orchestrator,
        "remediation_result",
    )


def test_orchestrator_does_not_manage_workflow():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "workflow",
    )

    assert not hasattr(
        orchestrator,
        "technician_workflow",
    )


def test_orchestrator_forwards_evidence_unchanged():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    evidence = {
        "network": {
            "connected": False,
            "adapter": "Ethernet",
        }
    }

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence=evidence,
    )

    dispatcher.dispatch.assert_called_once_with(
        "NETWORK",
        evidence=evidence,
    )


def test_orchestrator_supports_process_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "diagnosis": {
            "status": "NORMAL",
        }
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    returned_case = orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    dispatcher.dispatch.assert_called_once_with(
        "PROCESS",
        evidence=None,
    )

    assert returned_case is case


def test_orchestrator_supports_memory_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "memory_intelligence": {
            "severity": "WARNING",
        }
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    returned_case = orchestrator.investigate(
        case=case,
        domain="MEMORY",
    )

    dispatcher.dispatch.assert_called_once_with(
        "MEMORY",
        evidence=None,
    )

    assert returned_case is case


def test_orchestrator_normalizes_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain=" network ",
        evidence={},
    )

    dispatcher.dispatch.assert_called_once_with(
        " network ",
        evidence={},
    )


def test_orchestrator_does_not_modify_diagnostic_result():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    result = {
        "findings": [
            {
                "severity": "WARNING",
            }
        ]
    }

    dispatcher.dispatch.return_value = result

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert result == {
        "findings": [
            {
                "severity": "WARNING",
            }
        ]
    }


def test_orchestrator_uses_existing_coordinator():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()
    coordinator = Mock()

    diagnostic_result = {
        "findings": [],
    }

    dispatcher.dispatch.return_value = (
        diagnostic_result
    )

    orchestrator.dispatcher = dispatcher
    orchestrator.coordinator = coordinator

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    coordinator.attach_result.assert_called_once()

    attached_case, attached_result = (
        coordinator.attach_result.call_args.args
    )

    assert attached_case is case

    assert isinstance(
        attached_result,
        WindowsDiagnosticResult,
    )

    assert attached_result.findings == []


def test_orchestrator_does_not_change_case_lifecycle():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    lifecycle_before = case.lifecycle_state
    status_before = case.status

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert case.lifecycle_state == lifecycle_before
    assert case.status == status_before


def test_orchestrator_does_not_change_case_authorization():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    dispatcher = Mock()

    dispatcher.dispatch.return_value = {
        "findings": [],
    }

    orchestrator.dispatcher = dispatcher

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="NETWORK",
        evidence={},
    )

    assert not hasattr(
        case,
        "authorization_status",
    )