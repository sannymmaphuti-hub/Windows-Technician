from dataclasses import dataclass

import pytest

from engine.reliability_metrics import ReliabilityMetricsCollector


@dataclass
class Operation:
    operation_id: str
    status: str
    category: str | None = None


@dataclass
class RecoveryEntry:
    plan_id: str
    operation_id: str
    status: str


class ReliabilityServiceStub:
    def __init__(self, projection):
        self._projection = projection
        self.read_count = 0

    def projection(self):
        self.read_count += 1
        return self._projection


def test_empty_reliability_projection_returns_zero_counts():
    service = ReliabilityServiceStub({
        "operations": {"records": []},
        "recovery_history": {"total": 0, "by_status": {}, "entries": []},
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["failed_operation_count"] == 0
    assert result["failure_categories"] == {}
    assert result["retry_decision_count"] == 0
    assert result["recovery_record_count"] == 0
    assert result["recovery_approved_count"] == 0
    assert result["recovery_denied_count"] == 0
    assert result["recovery_executed_count"] == 0


def test_failed_operations_are_counted_by_category():
    service = ReliabilityServiceStub({
        "operations": {
            "records": [
                Operation("a", "FAILED", "TIMEOUT"),
                Operation("b", "FAILED", "TIMEOUT"),
                Operation("c", "FAILED", "PERMISSION"),
                Operation("d", "SUCCEEDED"),
            ],
        },
        "recovery_history": {"total": 0, "by_status": {}, "entries": []},
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["failed_operation_count"] == 3
    assert result["failure_categories"] == {
        "PERMISSION": 1,
        "TIMEOUT": 2,
    }


def test_missing_failure_category_is_reported_as_unknown():
    service = ReliabilityServiceStub({
        "operations": {
            "records": [Operation("a", "FAILED")],
        },
        "recovery_history": {"total": 0, "by_status": {}, "entries": []},
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["failure_categories"] == {"UNKNOWN": 1}


def test_recovery_history_status_counts_are_preserved():
    service = ReliabilityServiceStub({
        "operations": {"records": []},
        "recovery_history": {
            "total": 3,
            "by_status": {
                "APPROVED": 1,
                "DENIED": 1,
                "PENDING": 1,
            },
            "entries": [],
        },
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["recovery_record_count"] == 3
    assert result["recovery_status_counts"] == {
        "APPROVED": 1,
        "DENIED": 1,
        "PENDING": 1,
    }
    assert result["recovery_approved_count"] == 1
    assert result["recovery_denied_count"] == 1
    assert result["recovery_executed_count"] == 0


def test_retry_decisions_are_counted_without_claiming_execution():
    service = ReliabilityServiceStub({
        "operations": {"records": []},
        "retry_decisions": {
            "total": 2,
            "by_status": {
                "ELIGIBLE": 1,
                "INELIGIBLE": 1,
            },
            "entries": [],
        },
        "recovery_history": {"total": 0, "by_status": {}, "entries": []},
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["retry_decision_count"] == 2
    assert result["retry_decision_counts"] == {
        "ELIGIBLE": 1,
        "INELIGIBLE": 1,
    }
    assert result["recovery_executed_count"] == 0


def test_recovery_entries_can_be_counted_from_records():
    service = ReliabilityServiceStub({
        "operations": {"records": []},
        "recovery_history": {
            "entries": [
                RecoveryEntry("p1", "o1", "APPROVED"),
                RecoveryEntry("p2", "o2", "DENIED"),
            ],
        },
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["recovery_record_count"] == 2
    assert result["recovery_status_counts"] == {
        "APPROVED": 1,
        "DENIED": 1,
    }
    assert result["recovery_approved_count"] == 1
    assert result["recovery_denied_count"] == 1


def test_projection_returns_fresh_nested_mappings():
    service = ReliabilityServiceStub({
        "operations": {
            "by_status": {"FAILED": 2},
            "records": [],
        },
        "recovery_history": {
            "total": 1,
            "by_status": {"DENIED": 1},
            "entries": [],
        },
    })

    collector = ReliabilityMetricsCollector(service)
    first = collector.projection()
    first["operation_status_counts"]["FAILED"] = 999
    first["recovery_status_counts"]["DENIED"] = 999

    second = collector.projection()

    assert second["operation_status_counts"]["FAILED"] == 2
    assert second["recovery_status_counts"]["DENIED"] == 1


def test_source_records_are_not_modified():
    operation = Operation("a", "FAILED", "TIMEOUT")
    entry = RecoveryEntry("p1", "a", "DENIED")
    service = ReliabilityServiceStub({
        "operations": {"records": [operation]},
        "recovery_history": {"entries": [entry]},
    })

    ReliabilityMetricsCollector(service).projection()

    assert operation.status == "FAILED"
    assert operation.category == "TIMEOUT"
    assert entry.status == "DENIED"


def test_reads_existing_service_projection_once_per_call():
    service = ReliabilityServiceStub({
        "operations": {"records": []},
        "recovery_history": {"entries": []},
    })

    collector = ReliabilityMetricsCollector(service)
    assert service.read_count == 0

    collector.projection()
    assert service.read_count == 1

    collector.projection()
    assert service.read_count == 2


def test_rejects_missing_service():
    with pytest.raises(TypeError, match="required"):
        ReliabilityMetricsCollector(None)


def test_rejects_provider_without_projection():
    with pytest.raises(TypeError, match="projection"):
        ReliabilityMetricsCollector(object())


def test_rejects_invalid_projection():
    service = ReliabilityServiceStub(["not", "a", "mapping"])

    with pytest.raises(TypeError, match="must return a mapping"):
        ReliabilityMetricsCollector(service).projection()


def test_malformed_optional_sections_are_handled_safely():
    service = ReliabilityServiceStub({
        "operations": None,
        "recovery_history": None,
        "retry_decisions": None,
    })

    result = ReliabilityMetricsCollector(service).projection()

    assert result["operation_status_counts"] == {}
    assert result["recovery_status_counts"] == {}
    assert result["retry_decision_counts"] == {}
