import pytest

from ui.design_system import Severity
from ui.system_health_presentation import SystemHealthPresentation


def test_critical_findings_are_presented_first():
    result = SystemHealthPresentation().build(
        health_status="WARNING",
        findings=[
            {"title": "Informational event", "severity": "INFO"},
            {"title": "Critical failure", "severity": "CRITICAL"},
            {"title": "Warning event", "severity": "WARNING"},
        ],
    )

    assert result["highest_severity"] == Severity.CRITICAL.value
    assert result["findings"][0]["title"] == "Critical failure"
    assert result["finding_count"] == 3


def test_severity_counts_include_all_defined_levels():
    result = SystemHealthPresentation().build(
        health_status="HEALTHY",
        findings=[
            {"severity": "WARNING"},
            {"severity": "WARNING"},
            {"severity": "INFO"},
        ],
    )

    assert result["severity_counts"]["WARNING"] == 2
    assert result["severity_counts"]["INFO"] == 1
    assert result["severity_counts"]["CRITICAL"] == 0


def test_unknown_severity_is_preserved_as_unknown():
    result = SystemHealthPresentation().build(
        health_status="UNKNOWN",
        findings=[{"title": "Unclassified issue", "severity": "UNLISTED"}],
    )

    assert result["findings"][0]["severity"] == Severity.UNKNOWN.value
    assert result["highest_severity"] == Severity.UNKNOWN.value


def test_empty_findings_use_supplied_health_status():
    result = SystemHealthPresentation().build(
        health_status="HEALTHY",
        findings=[],
    )

    assert result["finding_count"] == 0
    assert result["highest_severity"] == Severity.HEALTHY.value


def test_source_findings_are_not_mutated():
    source = [{"title": "Memory pressure", "severity": "warning"}]

    SystemHealthPresentation().build(
        health_status="WARNING",
        findings=source,
    )

    assert source[0]["severity"] == "warning"


def test_rejects_invalid_inputs():
    presenter = SystemHealthPresentation()

    with pytest.raises(ValueError):
        presenter.build(health_status="", findings=[])

    with pytest.raises(TypeError):
        presenter.build(health_status="HEALTHY", findings="invalid")

    with pytest.raises(TypeError):
        presenter.build(health_status="HEALTHY", findings=[None])


def test_presentation_does_not_execute_operations():
    result = SystemHealthPresentation().build(
        health_status="WARNING",
        findings=[{"title": "Disk pressure", "severity": "WARNING"}],
    )

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False
