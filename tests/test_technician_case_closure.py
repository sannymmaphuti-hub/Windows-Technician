import pytest

from engine.technician_case_closure import (
    TechnicianCaseClosure,
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
def workflow():
    return TechnicianWorkflow(FakeCase())


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


def test_closure_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            None,
            "tech-001",
            "Issue resolved.",
        )


def test_closure_requires_technician_name(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            resolved_workflow,
            "",
            "Issue resolved.",
        )


def test_closure_requires_closure_reason(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            resolved_workflow,
            "tech-001",
            "",
        )


def test_case_must_be_resolved_before_closure(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow,
            "tech-001",
            "Issue resolved.",
        )


def test_closure_captures_case_identity(
    resolved_workflow,
):
    closure = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    assert closure.case_id == "case-001"
    assert closure.workflow_id == resolved_workflow.workflow_id


def test_closure_captures_technician_and_reason(
    resolved_workflow,
):
    closure = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Memory issue resolved and verified.",
    )

    assert closure.technician == "tech-001"
    assert (
        closure.reason
        == "Memory issue resolved and verified."
    )


def test_closure_captures_final_workflow_state(
    resolved_workflow,
):
    closure = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    assert closure.workflow_state is WorkflowState.RESOLVED


def test_closure_has_unique_id(
    resolved_workflow,
):
    first = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    second = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    assert first.closure_id != second.closure_id


def test_closure_has_timestamp(
    resolved_workflow,
):
    closure = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    assert closure.created_at is not None


def test_closure_does_not_mutate_workflow(
    resolved_workflow,
):
    original_state = resolved_workflow.state
    original_history = resolved_workflow.history

    TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    assert resolved_workflow.state is original_state
    assert resolved_workflow.history == original_history


def test_closure_properties_are_read_only(
    resolved_workflow,
):
    closure = TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved.",
    )

    with pytest.raises(AttributeError):
        closure.closure_id = "changed"

    with pytest.raises(AttributeError):
        closure.reason = "changed"


def test_whitespace_technician_is_rejected(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            resolved_workflow,
            "   ",
            "Issue resolved.",
        )


def test_whitespace_reason_is_rejected(
    resolved_workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            resolved_workflow,
            "tech-001",
            "   ",
        )