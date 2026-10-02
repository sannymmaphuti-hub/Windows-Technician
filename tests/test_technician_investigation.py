import uuid

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_investigation import TechnicianInvestigation
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def create_investigation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return case, workflow, TechnicianInvestigation(workflow)


def test_investigation_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianInvestigation(None)


def test_investigation_has_unique_id():
    _, workflow, _ = create_investigation()

    investigation_a = TechnicianInvestigation(workflow)
    investigation_b = TechnicianInvestigation(workflow)

    assert isinstance(investigation_a.investigation_id, str)
    assert isinstance(investigation_b.investigation_id, str)
    assert uuid.UUID(investigation_a.investigation_id)
    assert uuid.UUID(investigation_b.investigation_id)
    assert investigation_a.investigation_id != investigation_b.investigation_id


def test_investigation_starts_inactive():
    _, _, investigation = create_investigation()

    assert investigation.is_active is False
    assert investigation.is_complete is False


def test_investigation_can_start():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    assert investigation.is_active is True
    assert investigation.is_complete is False


def test_investigation_records_evidence_reviewed():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    evidence = {"source": "memory", "usage_percent": 91}
    investigation.review_evidence(evidence)

    assert investigation.evidence_reviewed == [evidence]


def test_investigation_records_findings_reviewed():
    case, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    finding = object()
    case.findings.append(finding)

    investigation.review_finding(finding)

    assert investigation.findings_reviewed == [finding]


def test_duplicate_evidence_is_not_recorded_twice():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    evidence = {"source": "cpu", "usage_percent": 95}

    investigation.review_evidence(evidence)
    investigation.review_evidence(evidence)

    assert investigation.evidence_reviewed == [evidence]


def test_duplicate_finding_is_not_recorded_twice():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    finding = object()

    investigation.review_finding(finding)
    investigation.review_finding(finding)

    assert investigation.findings_reviewed == [finding]


def test_evidence_cannot_be_reviewed_before_start():
    _, _, investigation = create_investigation()

    with pytest.raises(ValueError):
        investigation.review_evidence({"source": "memory"})


def test_finding_cannot_be_reviewed_before_start():
    _, _, investigation = create_investigation()

    with pytest.raises(ValueError):
        investigation.review_finding(object())


def test_investigation_can_complete():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()
    investigation.complete()

    assert investigation.is_active is False
    assert investigation.is_complete is True


def test_completed_investigation_cannot_be_modified():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()
    investigation.complete()

    with pytest.raises(ValueError):
        investigation.review_evidence({"source": "network"})

    with pytest.raises(ValueError):
        investigation.review_finding(object())


def test_investigation_cannot_complete_before_start():
    _, _, investigation = create_investigation()

    with pytest.raises(ValueError):
        investigation.complete()


def test_investigation_completion_advances_workflow():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()
    investigation.complete()

    assert workflow.state == WorkflowState.INVESTIGATING


def test_investigation_does_not_mutate_case_evidence():
    case, workflow, investigation = create_investigation()

    case.evidence["memory"] = {"usage_percent": 91}
    original_evidence = dict(case.evidence)

    workflow.start_investigation()
    investigation.start()

    investigation.review_evidence(case.evidence["memory"])

    assert case.evidence == original_evidence


def test_evidence_reviewed_is_externally_read_only():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    evidence = {"source": "storage", "free_gb": 12}
    investigation.review_evidence(evidence)

    reviewed = investigation.evidence_reviewed
    reviewed.clear()

    assert investigation.evidence_reviewed == [evidence]


def test_findings_reviewed_is_externally_read_only():
    _, workflow, investigation = create_investigation()

    workflow.start_investigation()
    investigation.start()

    finding = object()
    investigation.review_finding(finding)

    reviewed = investigation.findings_reviewed
    reviewed.clear()

    assert investigation.findings_reviewed == [finding]