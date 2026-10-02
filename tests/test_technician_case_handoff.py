import pytest

from engine.technician_case_handoff import TechnicianCaseHandoff
from engine.technician_workflow import TechnicianWorkflow


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def workflow():
    return TechnicianWorkflow(FakeCase())


@pytest.fixture
def handoff(workflow):
    return TechnicianCaseHandoff(
        workflow=workflow,
        from_technician="tech-001",
        to_technician="tech-002",
        reason="Requires further investigation.",
    )


def test_handoff_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow=None,
            from_technician="tech-001",
            to_technician="tech-002",
            reason="Further investigation required.",
        )


def test_handoff_exposes_workflow(
    handoff,
    workflow,
):
    assert handoff.workflow is workflow


def test_handoff_exposes_case_id(
    handoff,
):
    assert handoff.case_id == "case-001"


def test_handoff_exposes_sender(
    handoff,
):
    assert handoff.from_technician == "tech-001"


def test_handoff_exposes_receiver(
    handoff,
):
    assert handoff.to_technician == "tech-002"


def test_handoff_exposes_reason(
    handoff,
):
    assert handoff.reason == "Requires further investigation."


def test_handoff_has_unique_id(
    workflow,
):
    first = TechnicianCaseHandoff(
        workflow,
        "tech-001",
        "tech-002",
        "Reason one.",
    )

    second = TechnicianCaseHandoff(
        workflow,
        "tech-001",
        "tech-003",
        "Reason two.",
    )

    assert first.handoff_id != second.handoff_id


def test_handoff_has_utc_timestamp(
    handoff,
):
    assert handoff.created_at.tzinfo is not None
    assert handoff.created_at.utcoffset().total_seconds() == 0


def test_handoff_rejects_empty_sender(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            "",
            "tech-002",
            "Further investigation required.",
        )


def test_handoff_rejects_empty_receiver(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            "tech-001",
            "",
            "Further investigation required.",
        )


def test_handoff_rejects_empty_reason(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            "tech-001",
            "tech-002",
            "   ",
        )


def test_handoff_rejects_non_string_sender(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            123,
            "tech-002",
            "Further investigation required.",
        )


def test_handoff_rejects_non_string_receiver(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            "tech-001",
            123,
            "Further investigation required.",
        )


def test_handoff_rejects_non_string_reason(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseHandoff(
            workflow,
            "tech-001",
            "tech-002",
            None,
        )


def test_handoff_does_not_mutate_workflow(
    handoff,
    workflow,
):
    original_state = workflow.state
    original_history = workflow.history

    _ = handoff.handoff_id
    _ = handoff.created_at

    assert workflow.state is original_state
    assert workflow.history == original_history