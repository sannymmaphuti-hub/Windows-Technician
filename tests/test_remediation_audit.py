from engine.remediation_audit import RemediationAudit


def test_remediation_audit_starts_empty():
    audit = RemediationAudit()

    assert audit.get_records() == []


def test_remediation_audit_can_record_execution_result():
    audit = RemediationAudit()

    audit.record(
        action_id="memory_review",
        execution_status="EXECUTED",
    )

    records = audit.get_records()

    assert len(records) == 1
    assert records[0]["action_id"] == "memory_review"
    assert records[0]["execution_status"] == "EXECUTED"


def test_remediation_audit_can_record_failed_execution():
    audit = RemediationAudit()

    audit.record(
        action_id="memory_review",
        execution_status="FAILED",
    )

    records = audit.get_records()

    assert records[0]["action_id"] == "memory_review"
    assert records[0]["execution_status"] == "FAILED"


def test_remediation_audit_preserves_multiple_records():
    audit = RemediationAudit()

    audit.record(
        action_id="memory_review",
        execution_status="EXECUTED",
    )

    audit.record(
        action_id="test_action",
        execution_status="FAILED",
    )

    records = audit.get_records()

    assert len(records) == 2
    assert records[0]["action_id"] == "memory_review"
    assert records[1]["action_id"] == "test_action"

def test_remediation_audit_returns_copy_of_records():
    audit = RemediationAudit()

    audit.record(
        action_id="memory_review",
        execution_status="EXECUTED",
    )

    records = audit.get_records()

    records.clear()

    assert len(audit.get_records()) == 1


def test_remediation_audit_preserves_record_status():
    audit = RemediationAudit()

    audit.record(
        action_id="memory_review",
        execution_status="FAILED",
    )

    record = audit.get_records()[0]

    assert record["execution_status"] == "FAILED"