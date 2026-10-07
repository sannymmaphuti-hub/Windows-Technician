# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC DISPATCHER TESTS
# ==========================================


from unittest.mock import Mock

import pytest

from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)


def test_dispatcher_can_be_created():
    dispatcher = WindowsDiagnosticDispatcher()

    assert dispatcher is not None


def test_dispatch_process_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "PROCESS"

    dispatcher.adapters["PROCESS"] = adapter

    assert dispatcher.has_domain("PROCESS")


def test_dispatch_memory_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "MEMORY"

    dispatcher.adapters["MEMORY"] = adapter

    assert dispatcher.has_domain("MEMORY")


def test_dispatch_network_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"

    dispatcher.adapters["NETWORK"] = adapter

    assert dispatcher.has_domain("NETWORK")


def test_domain_lookup_is_case_insensitive():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"

    dispatcher.adapters["NETWORK"] = adapter

    assert dispatcher.has_domain("network")


def test_domain_lookup_ignores_whitespace():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"

    dispatcher.adapters["NETWORK"] = adapter

    assert dispatcher.has_domain(" network ")


def test_unknown_domain_is_not_available():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not dispatcher.has_domain("UNKNOWN")


def test_none_domain_is_not_available():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not dispatcher.has_domain(None)


def test_empty_domain_is_not_available():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not dispatcher.has_domain("")


def test_get_adapter_returns_registered_adapter():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"

    dispatcher.adapters["NETWORK"] = adapter

    result = dispatcher.get_adapter("NETWORK")

    assert result is adapter


def test_get_adapter_normalizes_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"

    dispatcher.adapters["NETWORK"] = adapter

    result = dispatcher.get_adapter(" network ")

    assert result is adapter


def test_get_unknown_adapter_returns_none():
    dispatcher = WindowsDiagnosticDispatcher()

    assert dispatcher.get_adapter("UNKNOWN") is None


def test_dispatch_requires_supported_implemented_domain():
    dispatcher = WindowsDiagnosticDispatcher()

    with pytest.raises(ValueError):
        dispatcher.dispatch(
            "UNKNOWN"
        )


def test_dispatch_calls_adapter_execute():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"
    adapter.execute.return_value = {
        "findings": []
    }

    dispatcher.adapters["NETWORK"] = adapter

    result = dispatcher.dispatch(
        "NETWORK",
        evidence={
            "network": {
                "connected": True
            }
        },
    )

    adapter.execute.assert_called_once_with(
        evidence={
            "network": {
                "connected": True
            }
        }
    )

    assert result == {
        "findings": []
    }


def test_dispatch_returns_existing_result_unchanged():
    dispatcher = WindowsDiagnosticDispatcher()

    expected_result = {
        "observations": [],
        "signals": [],
        "findings": [],
        "correlations": [],
        "candidates": [],
        "evaluations": [],
        "primary_cause": None,
        "confidences": [],
        "explanations": [],
        "recommendation": None,
    }

    adapter = Mock()
    adapter.domain = "NETWORK"
    adapter.execute.return_value = expected_result

    dispatcher.adapters["NETWORK"] = adapter

    result = dispatcher.dispatch(
        "NETWORK",
        evidence={},
    )

    assert result is expected_result


def test_dispatch_without_evidence_forwards_none():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "PROCESS"
    adapter.execute.return_value = {
        "diagnosis": {}
    }

    dispatcher.adapters["PROCESS"] = adapter

    result = dispatcher.dispatch(
        "PROCESS"
    )

    adapter.execute.assert_called_once_with(
        evidence=None
    )

    assert result == {
        "diagnosis": {}
    }


def test_dispatch_does_not_create_diagnostic_case():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not hasattr(
        dispatcher,
        "case",
    )

    assert not hasattr(
        dispatcher,
        "diagnostic_case",
    )


def test_dispatch_does_not_authorize_remediation():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not hasattr(
        dispatcher,
        "authorized",
    )

    assert not hasattr(
        dispatcher,
        "authorization_status",
    )


def test_dispatch_does_not_execute_remediation():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not hasattr(
        dispatcher,
        "execute_remediation",
    )

    assert not hasattr(
        dispatcher,
        "remediation_result",
    )


def test_dispatcher_does_not_own_workflow():
    dispatcher = WindowsDiagnosticDispatcher()

    assert not hasattr(
        dispatcher,
        "workflow",
    )

    assert not hasattr(
        dispatcher,
        "technician_workflow",
    )


def test_dispatcher_does_not_modify_registered_adapter():
    dispatcher = WindowsDiagnosticDispatcher()

    adapter = Mock()
    adapter.domain = "NETWORK"
    adapter.execute.return_value = {}

    dispatcher.adapters["NETWORK"] = adapter

    before = dispatcher.get_adapter("NETWORK")

    dispatcher.dispatch(
        "NETWORK",
        evidence={},
    )

    after = dispatcher.get_adapter("NETWORK")

    assert before is after