from engine.remediation_action import RemediationAction
from engine.remediation_audit import RemediationAudit
from engine.remediation_coordinator import RemediationCoordinator
from engine.remediation_operation import RemediationOperation


def test_coordinator_records_successful_execution_in_audit():
    audit = RemediationAudit()
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory-intensive processes.",
        handler=lambda: None,
    )

    action.authorize()

    coordinator.audit = audit

    coordinator.execute(action)

    records = audit.get_records()

    assert len(records) == 1
    assert records[0]["action_id"] == "memory_review"
    assert records[0]["execution_status"] == "EXECUTED"


def test_coordinator_records_failed_execution_in_audit():
    audit = RemediationAudit()
    coordinator = RemediationCoordinator()

    def failing_operation():
        raise RuntimeError("Remediation failed.")

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory-intensive processes.",
        handler=failing_operation,
    )

    action.authorize()

    coordinator.audit = audit

    coordinator.execute(action)

    records = audit.get_records()

    assert len(records) == 1
    assert records[0]["action_id"] == "memory_review"
    assert records[0]["execution_status"] == "FAILED"

def test_coordinator_records_unauthorized_execution_attempt():
    audit = RemediationAudit()
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory-intensive processes.",
        handler=lambda: None,
    )

    coordinator.audit = audit

    result = coordinator.execute(action)

    records = audit.get_records()

    assert result.execution_status == "NOT_EXECUTED"
    assert len(records) == 1
    assert records[0]["action_id"] == "memory_review"
    assert records[0]["execution_status"] == "NOT_EXECUTED"

def test_coordinator_records_execution_reason_in_audit():
    audit = RemediationAudit()
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory-intensive processes.",
        handler=lambda: None,
    )

    coordinator.audit = audit

    coordinator.execute(action)

    records = audit.get_records()

    assert records[0]["reason"] == "NOT_AUTHORIZED"

def test_coordinator_records_verification_result_in_audit():
    audit = RemediationAudit()
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory-intensive processes.",
        handler=lambda: None,
    )

    action.authorize()

    coordinator.audit = audit

    coordinator.execute(
        action,
        expected={"memory_usage": 50},
        observed={"memory_usage": 50},
    )

    records = audit.get_records()

    assert len(records) == 1
    assert records[0]["verification_result"]["verified"] is True
    assert records[0]["verification_result"]["action_id"] == "memory_review"