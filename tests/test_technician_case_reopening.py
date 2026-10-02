import pytest

from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def resolved_workflow():
    workflow = TechnicianWorkflow(FakeCase())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def closure(resolved_workflow):
    return TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved and verified.",
    )


def test_reopening_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseReopening(
            None,
            "tech-001",
            "New evidence received.",
        )


def test_reopening_requires_technician(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseReopening(
            resolved_workflow,
            "",
            "New evidence received.",
        )


def test_reopening_requires_reason(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseReopening(
            resolved_workflow,
            "tech-001",
            "",
        )


def test_only_resolved_case_can_be_reopened(
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert reopening.workflow_state is WorkflowState.RESOLVED


def test_reopening_captures_case_identity(
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert reopening.case_id == "case-001"
    assert reopening.workflow_id == resolved_workflow.workflow_id


def test_reopening_captures_technician_and_reason(
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert reopening.technician == "tech-001"
    assert reopening.reason == "New evidence received."


def test_reopening_has_unique_id(
    resolved_workflow,
):
    first = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    second = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert first.reopening_id != second.reopening_id


def test_reopening_has_timestamp(
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert reopening.created_at is not None


def test_reopening_preserves_closure_record(
    resolved_workflow,
    closure,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
        closure=closure,
    )

    assert reopening.closure is closure


def test_reopening_does_not_mutate_workflow(
    resolved_workflow,
):
    original_state = resolved_workflow.state
    original_history = resolved_workflow.history

    TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    assert resolved_workflow.state is original_state
    assert resolved_workflow.history == original_history


def test_reopening_properties_are_read_only(
    resolved_workflow,
):
    reopening = TechnicianCaseReopening(
        resolved_workflow,
        "tech-001",
        "New evidence received.",
    )

    with pytest.raises(AttributeError):
        reopening.reopening_id = "changed"

    with pytest.raises(AttributeError):
        reopening.reason = "changed"


def test_whitespace_technician_is_rejected(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseReopening(
            resolved_workflow,
            "   ",
            "New evidence received.",
        )


def test_whitespace_reason_is_rejected(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseReopening(
            resolved_workflow,
            "tech-001",
            "   ",
        )