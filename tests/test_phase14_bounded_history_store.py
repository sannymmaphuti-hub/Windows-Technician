from concurrent.futures import ThreadPoolExecutor

import pytest

from engine.bounded_history_store import BoundedHistoryStore


def test_history_retains_only_newest_records():
    history = BoundedHistoryStore(capacity=3)

    for value in range(5):
        history.append({"value": value})

    snapshot = history.projection()

    assert snapshot["capacity"] == 3
    assert snapshot["record_count"] == 3
    assert snapshot["evicted_count"] == 2
    assert [record["value"] for record in snapshot["records"]] == [2, 3, 4]


def test_record_is_detached_when_appended():
    history = BoundedHistoryStore(capacity=3)
    record = {"details": {"items": [1, 2]}}

    history.append(record)
    record["details"]["items"].append(3)

    assert history.snapshot()[0]["details"]["items"] == [1, 2]


def test_snapshot_mutation_does_not_change_internal_history():
    history = BoundedHistoryStore(capacity=3)
    history.append({"details": {"value": 10}})

    first = history.snapshot()
    first[0]["details"]["value"] = 999
    first.clear()

    second = history.snapshot()

    assert len(second) == 1
    assert second[0]["details"]["value"] == 10


def test_capacity_one_retains_exactly_one_record():
    history = BoundedHistoryStore(capacity=1)

    history.extend(["first", "second", "third"])

    snapshot = history.projection()

    assert snapshot["records"] == ["third"]
    assert snapshot["record_count"] == 1
    assert snapshot["evicted_count"] == 2


@pytest.mark.parametrize("capacity", [0, -1])
def test_non_positive_capacity_is_rejected(capacity):
    with pytest.raises(ValueError):
        BoundedHistoryStore(capacity=capacity)


@pytest.mark.parametrize("capacity", [True, 1.5, "10"])
def test_non_integer_capacity_is_rejected(capacity):
    with pytest.raises(TypeError):
        BoundedHistoryStore(capacity=capacity)


def test_initial_records_obey_capacity_and_eviction_rules():
    history = BoundedHistoryStore(
        capacity=2,
        initial_records=[1, 2, 3, 4],
    )

    snapshot = history.projection()

    assert snapshot["records"] == [3, 4]
    assert snapshot["record_count"] == 2
    assert snapshot["evicted_count"] == 2


def test_clear_removes_records_without_resetting_eviction_count():
    history = BoundedHistoryStore(capacity=2)
    history.extend([1, 2, 3])

    removed = history.clear()
    snapshot = history.projection()

    assert removed == 2
    assert snapshot["record_count"] == 0
    assert snapshot["evicted_count"] == 1


def test_concurrent_appends_never_exceed_capacity():
    capacity = 25
    history = BoundedHistoryStore(capacity=capacity)

    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(history.append, range(500)))

    snapshot = history.projection()

    assert snapshot["record_count"] == capacity
    assert len(snapshot["records"]) == capacity
    assert snapshot["evicted_count"] == 500 - capacity


def test_projection_is_independent_between_reads():
    history = BoundedHistoryStore(capacity=3)
    history.append({"value": 1})

    first = history.projection()
    first["records"][0]["value"] = 999

    second = history.projection()

    assert second["records"][0]["value"] == 1


def test_clear_on_empty_history_is_safe():
    history = BoundedHistoryStore(capacity=2)

    assert history.clear() == 0
    assert history.snapshot() == []
    assert history.projection()["evicted_count"] == 0
