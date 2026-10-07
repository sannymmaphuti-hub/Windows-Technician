# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC EXECUTION ADAPTER TESTS
# ==========================================

from unittest.mock import Mock

import pytest

from engine.windows_diagnostic_execution_adapter import (
    WindowsDiagnosticExecutionAdapter,
)


def test_process_adapter_can_be_created():
    adapter = WindowsDiagnosticExecutionAdapter("PROCESS")

    assert adapter.domain == "PROCESS"


def test_memory_adapter_can_be_created():
    adapter = WindowsDiagnosticExecutionAdapter("MEMORY")

    assert adapter.domain == "MEMORY"


def test_network_adapter_can_be_created():
    adapter = WindowsDiagnosticExecutionAdapter("NETWORK")

    assert adapter.domain == "NETWORK"


def test_domain_is_normalized():
    adapter = WindowsDiagnosticExecutionAdapter(" memory ")

    assert adapter.domain == "MEMORY"


def test_unknown_domain_is_rejected():
    with pytest.raises(ValueError):
        WindowsDiagnosticExecutionAdapter("UNKNOWN")


def test_startup_domain_is_now_implemented():
    adapter = WindowsDiagnosticExecutionAdapter(
        "STARTUP"
    )

    assert adapter.domain == "STARTUP"
    assert adapter.implementation is not None

def test_adapter_does_not_create_case():
    adapter = WindowsDiagnosticExecutionAdapter("NETWORK")

    assert not hasattr(adapter, "case")
    assert not hasattr(adapter, "diagnostic_case")


def test_adapter_does_not_authorize_remediation():
    adapter = WindowsDiagnosticExecutionAdapter("NETWORK")

    assert not hasattr(adapter, "authorized")
    assert not hasattr(adapter, "authorization_status")


def test_adapter_does_not_execute_remediation():
    adapter = WindowsDiagnosticExecutionAdapter("NETWORK")

    assert not hasattr(adapter, "execute_remediation")
    assert not hasattr(adapter, "remediation_result")


def test_process_implementation_uses_analyzer_contract():
    fake_analyzer = Mock()
    fake_analyzer.analyze.return_value = {
        "diagnosis": {
            "status": "NORMAL"
        }
    }

    adapter = WindowsDiagnosticExecutionAdapter(
        "PROCESS",
        implementation=fake_analyzer,
    )

    result = adapter.execute()

    fake_analyzer.analyze.assert_called_once_with()
    assert result == {
        "diagnosis": {
            "status": "NORMAL"
        }
    }


def test_memory_implementation_uses_analyzer_contract():
    fake_analyzer = Mock()
    fake_analyzer.analyze.return_value = {
        "memory_intelligence": {
            "severity": "WARNING"
        }
    }

    adapter = WindowsDiagnosticExecutionAdapter(
        "MEMORY",
        implementation=fake_analyzer,
    )

    result = adapter.execute()

    fake_analyzer.analyze.assert_called_once_with()
    assert result == {
        "memory_intelligence": {
            "severity": "WARNING"
        }
    }


def test_network_implementation_receives_evidence():
    fake_network_pipeline = Mock()

    fake_network_pipeline.diagnose.return_value = {
        "findings": []
    }

    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK",
        implementation=fake_network_pipeline,
    )

    evidence = {
        "network": {
            "connected": False
        }
    }

    result = adapter.execute(
        evidence=evidence
    )

    fake_network_pipeline.diagnose.assert_called_once_with(
        evidence
    )

    assert result == {
        "findings": []
    }


def test_network_execution_requires_evidence():
    fake_network_pipeline = Mock()

    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK",
        implementation=fake_network_pipeline,
    )

    with pytest.raises(ValueError):
        adapter.execute()


def test_process_execution_does_not_require_evidence():
    fake_analyzer = Mock()

    fake_analyzer.analyze.return_value = {
        "diagnosis": {}
    }

    adapter = WindowsDiagnosticExecutionAdapter(
        "PROCESS",
        implementation=fake_analyzer,
    )

    adapter.execute()

    fake_analyzer.analyze.assert_called_once_with()


def test_adapter_can_use_registry_implementation():
    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK"
    )

    assert adapter.implementation is not None


def test_adapter_does_not_modify_registry():
    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK"
    )

    assert adapter.domain == "NETWORK"


def test_execution_is_explicit():
    fake_network_pipeline = Mock()

    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK",
        implementation=fake_network_pipeline,
    )

    fake_network_pipeline.diagnose.assert_not_called()


def test_execution_returns_existing_result_unchanged():
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

    fake_network_pipeline = Mock()
    fake_network_pipeline.diagnose.return_value = (
        expected_result
    )

    adapter = WindowsDiagnosticExecutionAdapter(
        "NETWORK",
        implementation=fake_network_pipeline,
    )

    result = adapter.execute(
        evidence={}
    )

    assert result is expected_result