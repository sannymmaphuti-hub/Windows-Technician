# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATION
# COORDINATOR TESTS
# ==========================================

from unittest.mock import Mock

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_investigation_coordinator import (
    WindowsDiagnosticInvestigationCoordinator,
)


def test_coordinator_can_be_created():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    assert coordinator is not None


def test_coordinator_requires_case():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    with pytest.raises(ValueError):
        coordinator.attach_result(
            None,
            {
                "findings": [],
            },
        )


def test_coordinator_requires_result():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    with pytest.raises(ValueError):
        coordinator.attach_result(
            case,
            None,
        )


def test_coordinator_attaches_findings():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "findings": [
            {
                "category": "NETWORK",
                "severity": "WARNING",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert case.findings == result["findings"]


def test_coordinator_attaches_observations():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "observations": [
            {
                "category": "NETWORK",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert case.observations == result["observations"]


def test_coordinator_attaches_signals():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "signals": [
            {
                "name": "NETWORK_DISCONNECTED",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert case.signals == result["signals"]


def test_coordinator_attaches_correlations():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "correlations": [
            {
                "type": "NETWORK_FAILURE",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert case.correlations == result["correlations"]


def test_coordinator_attaches_root_cause_candidates():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "candidates": [
            {
                "category": "NETWORK",
                "explanation": "Network connectivity is unavailable.",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert (
        case.root_cause_candidates
        == result["candidates"]
    )


def test_coordinator_attaches_primary_root_cause():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "primary_cause": {
            "category": "NETWORK",
            "explanation": "Network connectivity is unavailable.",
        }
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert (
        case.primary_root_cause
        == result["primary_cause"]
    )


def test_coordinator_does_not_require_every_result_field():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "findings": [],
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert case.findings == []
    assert case.observations == []
    assert case.signals == []


def test_coordinator_preserves_case_identity():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()
    case_id = case.case_id

    coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert case.case_id == case_id


def test_coordinator_does_not_create_new_case():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    returned_case = coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert returned_case is case


def test_coordinator_does_not_authorize_remediation():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert not hasattr(
        coordinator,
        "authorized",
    )

    assert not hasattr(
        coordinator,
        "authorization_status",
    )


def test_coordinator_does_not_execute_remediation():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert not hasattr(
        coordinator,
        "execute_remediation",
    )

    assert not hasattr(
        coordinator,
        "remediation_result",
    )


def test_coordinator_does_not_manage_workflow():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert not hasattr(
        coordinator,
        "workflow",
    )

    assert not hasattr(
        coordinator,
        "technician_workflow",
    )


def test_coordinator_does_not_mutate_result():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    result = {
        "findings": [
            {
                "severity": "WARNING",
            }
        ]
    }

    original_result = {
        "findings": [
            {
                "severity": "WARNING",
            }
        ]
    }

    coordinator.attach_result(
        case,
        result,
    )

    assert result == original_result


def test_coordinator_uses_case_setters():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = Mock(spec=DiagnosticCase)

    result = {
        "observations": [],
        "signals": [],
        "findings": [],
        "correlations": [],
        "candidates": [],
        "primary_cause": None,
    }

    coordinator.attach_result(
        case,
        result,
    )

    case.set_observations.assert_called_once_with([])
    case.set_signals.assert_called_once_with([])
    case.set_findings.assert_called_once_with([])
    case.set_correlations.assert_called_once_with([])
    case.set_root_cause_candidates.assert_called_once_with([])
    case.set_primary_root_cause.assert_called_once_with(
        None
    )


def test_coordinator_does_not_change_case_lifecycle():
    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    case = DiagnosticCase()

    lifecycle_before = case.lifecycle_state
    status_before = case.status

    coordinator.attach_result(
        case,
        {
            "findings": [],
        },
    )

    assert case.lifecycle_state == lifecycle_before
    assert case.status == status_before