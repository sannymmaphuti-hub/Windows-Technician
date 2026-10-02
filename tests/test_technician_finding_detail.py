from types import SimpleNamespace

import pytest

from engine.finding import Finding
from engine.technician_finding_detail import (
    TechnicianFindingDetail,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


def create_workflow():
    case = SimpleNamespace(
        case_id="CASE-001",
        evidence={
            "memory": "High memory usage",
        },
        findings=[],
        correlations=[],
    )

    return TechnicianWorkflow(case)


def create_finding():
    signal = SimpleNamespace(
        signal_type="MEMORY_PRESSURE",
    )

    return Finding(
        "MEMORY_PRESSURE",
        "MEMORY",
        "HIGH",
        "High memory usage detected.",
        [signal],
    )


def create_detail():
    workflow = create_workflow()

    cycle_history = TechnicianRecoveryCycleHistory(
        workflow
    )

    finding = create_finding()
    workflow.case.findings.append(finding)

    detail = TechnicianFindingDetail(
        workflow,
        cycle_history,
        finding,
    )

    return (
        detail,
        workflow,
        cycle_history,
        finding,
    )


def test_requires_workflow():
    workflow = create_workflow()
    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    with pytest.raises(ValueError):
        TechnicianFindingDetail(
            None,
            history,
            create_finding(),
        )


def test_requires_cycle_history():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        TechnicianFindingDetail(
            workflow,
            None,
            create_finding(),
        )


def test_requires_finding():
    workflow = create_workflow()
    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    with pytest.raises(ValueError):
        TechnicianFindingDetail(
            workflow,
            history,
            None,
        )


def test_cycle_history_must_belong_to_workflow():
    workflow = create_workflow()
    other_workflow = create_workflow()

    history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianFindingDetail(
            workflow,
            history,
            create_finding(),
        )


def test_finding_must_belong_to_workflow_case():
    workflow = create_workflow()
    other_finding = create_finding()

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    with pytest.raises(ValueError):
        TechnicianFindingDetail(
            workflow,
            history,
            other_finding,
        )


def test_exposes_workflow():
    detail, workflow, _, _ = create_detail()

    assert detail.workflow is workflow


def test_exposes_cycle_history():
    detail, _, history, _ = create_detail()

    assert detail.cycle_history is history


def test_exposes_finding():
    detail, _, _, finding = create_detail()

    assert detail.finding is finding


def test_exposes_finding_type():
    detail, _, _, finding = create_detail()

    assert detail.finding_type == finding.finding_type


def test_exposes_description():
    detail, _, _, finding = create_detail()

    assert detail.description == finding.description


def test_exposes_category():
    detail, _, _, finding = create_detail()

    assert detail.category == finding.category


def test_exposes_severity():
    detail, _, _, finding = create_detail()

    assert detail.severity == finding.severity


def test_exposes_supporting_signals():
    detail, _, _, finding = create_detail()

    assert (
        detail.supporting_signals
        == finding.supporting_signals
    )


def test_supporting_signals_are_read_only():
    detail, _, _, finding = create_detail()

    signals = detail.supporting_signals
    signals.clear()

    assert len(finding.supporting_signals) == 1


def test_finding_reference_is_preserved():
    detail, _, _, finding = create_detail()

    assert detail.finding is finding