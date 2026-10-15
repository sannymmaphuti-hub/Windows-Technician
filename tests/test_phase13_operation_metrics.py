from dataclasses import dataclass
from enum import Enum

import pytest

from engine.operation_metrics import OperationMetricsCollector


class Status(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class Record:
    operation_id: str
    status: object


class Tracker:
    def __init__(self, records):
        self.records = records


def collector_for(*statuses):
    records = [
        Record(f"operation-{index}", status)
        for index, status in enumerate(statuses)
    ]
    return OperationMetricsCollector(Tracker(records))


def test_empty_tracker_returns_zero_metrics():
    result = OperationMetricsCollector(Tracker([])).projection()

    assert result["total_operations"] == 0
    assert result["terminal_count"] == 0
    assert result["success_rate"] == 0.0
    assert result["failure_rate"] == 0.0
    assert result["completion_rate"] == 0.0
    assert result["unknown_status_count"] == 0


def test_counts_each_known_status():
    result = collector_for(
        Status.PENDING,
        Status.RUNNING,
        Status.SUCCEEDED,
        Status.FAILED,
        Status.CANCELLED,
    ).projection()

    assert result["total_operations"] == 5
    assert result["by_status"] == {
        "PENDING": 1,
        "RUNNING": 1,
        "SUCCEEDED": 1,
        "FAILED": 1,
        "CANCELLED": 1,
    }
    assert result["pending_count"] == 1
    assert result["running_count"] == 1
    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1
    assert result["cancelled_count"] == 1


def test_completion_rate_uses_terminal_operations():
    result = collector_for(
        Status.SUCCEEDED,
        Status.FAILED,
        Status.RUNNING,
        Status.PENDING,
    ).projection()

    assert result["terminal_count"] == 2
    assert result["completion_rate"] == 0.5


def test_success_and_failure_rates_use_terminal_operations():
    result = collector_for(
        Status.SUCCEEDED,
        Status.SUCCEEDED,
        Status.FAILED,
        Status.CANCELLED,
        Status.RUNNING,
    ).projection()

    assert result["success_rate"] == pytest.approx(2 / 4)
    assert result["failure_rate"] == pytest.approx(1 / 4)


def test_cancelled_operations_are_terminal_but_not_failures():
    result = collector_for(Status.CANCELLED).projection()

    assert result["terminal_count"] == 1
    assert result["completion_rate"] == 1.0
    assert result["success_rate"] == 0.0
    assert result["failure_rate"] == 0.0


def test_status_strings_are_normalized():
    result = collector_for("succeeded", " FAILED ").projection()

    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1
    assert result["unknown_status_count"] == 0


def test_unknown_status_is_counted_without_crashing():
    result = collector_for("UNEXPECTED", None).projection()

    assert result["total_operations"] == 2
    assert result["unknown_status_count"] == 2
    assert result["terminal_count"] == 0


def test_mapping_records_are_supported():
    tracker = Tracker([
        {"status": "SUCCEEDED"},
        {"status": "FAILED"},
    ])

    result = OperationMetricsCollector(tracker).projection()

    assert result["total_operations"] == 2
    assert result["succeeded_count"] == 1
    assert result["failed_count"] == 1


def test_mapping_of_records_is_supported():
    tracker = Tracker({
        "a": Record("a", "SUCCEEDED"),
        "b": Record("b", "RUNNING"),
    })

    result = OperationMetricsCollector(tracker).projection()

    assert result["total_operations"] == 2
    assert result["succeeded_count"] == 1
    assert result["running_count"] == 1


def test_projection_is_detached_between_calls():
    collector = collector_for(Status.SUCCEEDED)

    first = collector.projection()
    first["by_status"]["SUCCEEDED"] = 500
    first["total_operations"] = 500

    second = collector.projection()

    assert second["by_status"]["SUCCEEDED"] == 1
    assert second["total_operations"] == 1


def test_metrics_do_not_modify_tracker_records():
    tracker = Tracker([
        Record("a", Status.SUCCEEDED),
        Record("b", Status.RUNNING),
    ])
    original = [(record.operation_id, record.status) for record in tracker.records]

    collector = OperationMetricsCollector(tracker)
    collector.projection()
    collector.projection()

    assert [(record.operation_id, record.status) for record in tracker.records] == original


def test_requires_tracker():
    with pytest.raises(TypeError, match="required"):
        OperationMetricsCollector(None)


def test_rejects_tracker_without_records():
    with pytest.raises(TypeError, match="records"):
        OperationMetricsCollector(object())


def test_rejects_non_iterable_records():
    with pytest.raises(TypeError, match="mapping or iterable"):
        OperationMetricsCollector(Tracker(42)).projection()
