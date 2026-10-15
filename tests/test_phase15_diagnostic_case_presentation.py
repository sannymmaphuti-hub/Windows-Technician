import pytest

from ui.diagnostic_case_presentation_model import DiagnosticCasePresentationModel


def test_projects_case_identity_lifecycle_and_summary():
    model = DiagnosticCasePresentationModel()

    result = model.build({
        "case_id": "case-123",
        "status": "OPEN",
        "state": "INVESTIGATING",
        "findings": [{"title": "High memory usage"}],
        "recommendations": ["Review memory-intensive applications"],
        "evidence": [{"source": "memory"}],
        "correlations": [{"signal_count": 2}],
        "root_causes": [{"category": "RESOURCE_PRESSURE"}],
    })

    assert result["identity"]["case_id"] == "case-123"
    assert result["lifecycle"] == {
        "status": "OPEN",
        "state": "INVESTIGATING",
    }
    assert result["summary"] == {
        "finding_count": 1,
        "recommendation_count": 1,
        "evidence_count": 1,
        "correlation_count": 1,
        "root_cause_count": 1,
    }


def test_projection_is_detached_from_source():
    source = {
        "case_id": "case-456",
        "findings": [{"title": "CPU pressure"}],
    }

    result = DiagnosticCasePresentationModel().build(source)
    result["findings"][0]["title"] = "Changed"
    result["identity"]["case_id"] = "changed"

    assert source["findings"][0]["title"] == "CPU pressure"
    assert source["case_id"] == "case-456"


def test_missing_sections_default_to_empty_collections():
    result = DiagnosticCasePresentationModel().build({"case_id": "case-789"})

    assert result["summary"]["finding_count"] == 0
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_rejects_non_mapping_input():
    with pytest.raises(TypeError, match="case_projection"):
        DiagnosticCasePresentationModel().build(None)


def test_rejects_invalid_collection_shape():
    with pytest.raises(TypeError, match="findings"):
        DiagnosticCasePresentationModel().build({"findings": "not-a-list"})


def test_presentation_does_not_execute_operations():
    result = DiagnosticCasePresentationModel().build({
        "case_id": "case-999",
        "findings": [{"title": "Disk pressure"}],
    })

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False
