import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_workflow import TechnicianWorkflow


@pytest.fixture
def resolved_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

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
        "Technician A",
        "Case resolved after verification.",
    )


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager, closure):
    return manager.request_reopening(
        "Technician B",
        "Issue returned after closure.",
        closure=closure,
    )


def test_audit_requires_workflow():
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    with pytest.raises(ValueError):
        TechnicianReopeningAudit(None)


def test_audit_starts_empty(resolved_workflow):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    assert audit.entries == []


def test_audit_records_reopening_request(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    entry = audit.record_request(reopening)

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "REQUESTED"
    assert entry["reopening_id"] == (
        reopening.reopening_id
    )
    assert entry["technician"] == (
        reopening.technician
    )
    assert entry["reason"] == reopening.reason


def test_audit_preserves_closure_reference(
    resolved_workflow,
    reopening,
    closure,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    entry = audit.record_request(reopening)

    assert entry["closure_id"] == closure.closure_id


def test_audit_records_accepted_status(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    entry = audit.record_status(lifecycle)

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "ACCEPTED"
    assert entry["reopening_id"] == (
        reopening.reopening_id
    )


def test_audit_records_rejected_status(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.reject_reopening(lifecycle)

    entry = audit.record_status(lifecycle)

    assert entry["status"] == "REJECTED"


def test_audit_records_completed_status(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)
    manager.complete_reopening(lifecycle)

    entry = audit.record_status(lifecycle)

    assert entry["status"] == "COMPLETED"


def test_audit_preserves_event_order(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    audit.record_request(reopening)

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    audit.record_status(lifecycle)

    assert [
        entry["status"]
        for entry in audit.entries
    ] == [
        "REQUESTED",
        "ACCEPTED",
    ]


def test_audit_entries_are_read_only(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    audit.record_request(reopening)

    entries = audit.entries
    entries.clear()

    assert len(audit.entries) == 1


def test_audit_rejects_foreign_reopening(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    foreign_case = DiagnosticCase()
    foreign_workflow = TechnicianWorkflow(
        foreign_case
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    foreign_manager = (
        TechnicianCaseReopeningManager(
            foreign_workflow
        )
    )

    with pytest.raises(ValueError):
        foreign_manager.request_reopening(
            "Technician C",
            "Foreign reopening.",
        )

    with pytest.raises(ValueError):
        audit.record_request(
            object()
        )


def test_audit_rejects_foreign_lifecycle(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    foreign_case = DiagnosticCase()
    foreign_workflow = TechnicianWorkflow(
        foreign_case
    )

    foreign_audit = TechnicianReopeningAudit(
        foreign_workflow
    )

    with pytest.raises(ValueError):
        foreign_audit.record_status(
            object()
        )


def test_audit_does_not_change_workflow(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_audit import (
        TechnicianReopeningAudit,
    )

    audit = TechnicianReopeningAudit(
        resolved_workflow
    )

    original_state = resolved_workflow.state
    original_history = resolved_workflow.history

    audit.record_request(reopening)

    assert resolved_workflow.state == original_state
    assert resolved_workflow.history == (
        original_history
    )