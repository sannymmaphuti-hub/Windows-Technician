import pytest

from engine.recommendation import Recommendation
from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
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
def recommendation():
    return Recommendation(
        "memory_review",
        "MEMORY",
        "HIGH",
        "Review memory-intensive processes.",
        "High memory usage may affect responsiveness.",
    )


@pytest.fixture
def activity_log(workflow):
    return TechnicianActivityLog(workflow)


def test_activity_log_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianActivityLog(None)


def test_activity_log_exposes_workflow(
    activity_log,
    workflow,
):
    assert activity_log.workflow is workflow


def test_activity_log_starts_empty(
    activity_log,
):
    assert activity_log.entries == []


def test_activity_log_records_workflow_transition(
    activity_log,
    workflow,
):
    workflow.start_investigation()

    activity_log.record_workflow_event()

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "WORKFLOW"
    assert activity_log.entries[0]["state"] is WorkflowState.INVESTIGATING


def test_activity_log_records_decision(
    activity_log,
    workflow,
    recommendation,
):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        notes="Proceed.",
    )

    activity_log.record_decision(decision)

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "DECISION"
    assert activity_log.entries[0]["decision"] is decision


def test_activity_log_records_note(
    activity_log,
    workflow,
):
    notes = TechnicianCaseNotes(workflow)
    note = notes.add_note("Investigation completed.")

    activity_log.record_note(note)

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "NOTE"
    assert activity_log.entries[0]["note"] is note


def test_activity_log_records_remediation(
    activity_log,
):
    activity_log.record_remediation("EXECUTED")

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "REMEDIATION"
    assert activity_log.entries[0]["status"] == "EXECUTED"


def test_activity_log_records_verification(
    activity_log,
):
    activity_log.record_verification(True)

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "VERIFICATION"
    assert activity_log.entries[0]["verified"] is True


def test_activity_log_records_escalation(
    activity_log,
):
    activity_log.record_escalation("ESCALATED")

    assert len(activity_log.entries) == 1
    assert activity_log.entries[0]["type"] == "ESCALATION"
    assert activity_log.entries[0]["status"] == "ESCALATED"


def test_activity_log_preserves_entry_order(
    activity_log,
    workflow,
):
    workflow.start_investigation()
    activity_log.record_workflow_event()

    activity_log.record_remediation("EXECUTED")
    activity_log.record_verification(True)

    assert [entry["type"] for entry in activity_log.entries] == [
        "WORKFLOW",
        "REMEDIATION",
        "VERIFICATION",
    ]


def test_activity_log_entries_are_read_only(
    activity_log,
):
    activity_log.record_remediation("EXECUTED")

    entries = activity_log.entries
    entries.clear()

    assert len(activity_log.entries) == 1


def test_activity_log_does_not_mutate_workflow(
    activity_log,
    workflow,
):
    workflow.start_investigation()
    original_history = workflow.history

    activity_log.record_workflow_event()

    assert workflow.history == original_history


def test_activity_log_supports_multiple_entries(
    activity_log,
):
    activity_log.record_remediation("EXECUTED")
    activity_log.record_verification(False)
    activity_log.record_escalation("ESCALATED")

    assert len(activity_log.entries) == 3