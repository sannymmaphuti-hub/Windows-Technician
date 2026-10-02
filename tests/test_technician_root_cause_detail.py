import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.root_cause import RootCauseCandidate
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_root_cause_detail import (
    TechnicianRootCauseDetail,
)
from engine.technician_workflow import TechnicianWorkflow


def create_detail():
    case = DiagnosticCase()

    root_cause = RootCauseCandidate(
        "Insufficient available memory",
        "MEMORY",
        0.90,
        evidence=["MEMORY_PRESSURE"],
        reason="Available memory is consistently low.",
    )

    case.root_causes.append(root_cause)

    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    detail = TechnicianRootCauseDetail(
        workflow,
        history,
        root_cause,
    )

    return detail, workflow, history, root_cause


def test_requires_workflow():
    _, _, history, root_cause = create_detail()

    with pytest.raises(ValueError):
        TechnicianRootCauseDetail(
            None,
            history,
            root_cause,
        )


def test_requires_cycle_history():
    _, workflow, _, root_cause = create_detail()

    with pytest.raises(ValueError):
        TechnicianRootCauseDetail(
            workflow,
            None,
            root_cause,
        )


def test_requires_matching_cycle_history():
    _, workflow, _, root_cause = create_detail()

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(other_case)
    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianRootCauseDetail(
            workflow,
            other_history,
            root_cause,
        )


def test_requires_root_cause():
    _, workflow, history, _ = create_detail()

    with pytest.raises(ValueError):
        TechnicianRootCauseDetail(
            workflow,
            history,
            None,
        )


def test_root_cause_must_belong_to_workflow_case():
    detail, workflow, history, _ = create_detail()

    other_root_cause = RootCauseCandidate(
        "CPU saturation",
        "CPU",
        0.70,
        evidence=["CPU_SPIKE"],
        reason="CPU usage is consistently elevated.",
    )

    with pytest.raises(ValueError):
        TechnicianRootCauseDetail(
            workflow,
            history,
            other_root_cause,
        )


def test_exposes_workflow():
    detail, workflow, _, _ = create_detail()

    assert detail.workflow is workflow


def test_exposes_cycle_history():
    detail, _, history, _ = create_detail()

    assert detail.cycle_history is history


def test_exposes_root_cause():
    detail, _, _, root_cause = create_detail()

    assert detail.root_cause is root_cause


def test_exposes_cause():
    detail, _, _, root_cause = create_detail()

    assert detail.cause == root_cause.cause


def test_exposes_category():
    detail, _, _, root_cause = create_detail()

    assert detail.category == root_cause.category


def test_exposes_confidence():
    detail, _, _, root_cause = create_detail()

    assert detail.confidence == root_cause.confidence


def test_exposes_confidence_level():
    detail, _, _, root_cause = create_detail()

    assert (
        detail.confidence_level
        == root_cause.confidence_level()
    )


def test_exposes_evidence():
    detail, _, _, root_cause = create_detail()

    assert detail.evidence == root_cause.evidence


def test_exposes_evidence_as_copy():
    detail, _, _, root_cause = create_detail()

    evidence = detail.evidence

    assert evidence == root_cause.evidence
    assert evidence is not root_cause.evidence


def test_exposes_reason():
    detail, _, _, root_cause = create_detail()

    assert detail.reason == root_cause.reason


def test_root_cause_reference_is_preserved():
    detail, _, _, root_cause = create_detail()

    assert detail.root_cause is root_cause