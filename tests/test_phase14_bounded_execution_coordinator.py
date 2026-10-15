from concurrent.futures import ThreadPoolExecutor

import pytest

from engine.performance_scale_boundary import PerformanceLimits
from engine.bounded_execution_coordinator import (
    BoundedExecutionCoordinator,
)


def make_coordinator(limit=3):
    return BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=limit,
            max_managed_machines=10,
            max_events_retained=20,
            max_projection_items=10,
        )
    )


def test_reservation_is_admitted_and_capacity_is_decremented():
    coordinator = make_coordinator(limit=3)

    result = coordinator.reserve(units=2)

    assert result.admitted is True
    assert result.reservation_id
    assert result.available_capacity == 1
    assert result.reason == "RESERVED"

    snapshot = coordinator.projection()

    assert snapshot["active_reservation_count"] == 1
    assert snapshot["active_units_by_resource"]["concurrent_diagnostics"] == 2
    assert snapshot["available_capacity_by_resource"]["concurrent_diagnostics"] == 1


def test_reservation_is_rejected_when_capacity_is_insufficient():
    coordinator = make_coordinator(limit=2)
    first = coordinator.reserve(units=2)

    result = coordinator.reserve(units=1)

    assert first.admitted is True
    assert result.admitted is False
    assert result.reservation_id is None
    assert result.available_capacity == 0
    assert result.reason == "CAPACITY_EXHAUSTED"


def test_completion_releases_capacity_exactly_once():
    coordinator = make_coordinator(limit=2)
    result = coordinator.reserve(units=2)

    assert coordinator.complete(result.reservation_id) is True
    assert coordinator.complete(result.reservation_id) is False

    snapshot = coordinator.projection()

    assert snapshot["active_reservation_count"] == 0
    assert snapshot["available_capacity_by_resource"]["concurrent_diagnostics"] == 2
    assert snapshot["history"][-1]["status"] == "COMPLETED"


def test_release_does_not_claim_work_completed():
    coordinator = make_coordinator()
    result = coordinator.reserve()

    assert coordinator.release(result.reservation_id) is True
    assert coordinator.release(result.reservation_id) is False

    snapshot = coordinator.projection()

    assert snapshot["active_reservation_count"] == 0
    assert snapshot["history"][-1]["status"] == "RELEASED"


def test_unknown_reservation_cannot_release_capacity():
    coordinator = make_coordinator()

    assert coordinator.complete("unknown-id") is False
    assert coordinator.release("unknown-id") is False
    assert coordinator.projection()["active_reservation_count"] == 0


def test_resources_have_independent_capacity_budgets():
    coordinator = make_coordinator(limit=2)

    diagnostic = coordinator.reserve(
        resource="concurrent_diagnostics",
        units=2,
    )
    machines = coordinator.reserve(
        resource="managed_machines",
        units=5,
    )

    assert diagnostic.admitted is True
    assert machines.admitted is True

    snapshot = coordinator.projection()

    assert snapshot["active_units_by_resource"]["concurrent_diagnostics"] == 2
    assert snapshot["active_units_by_resource"]["managed_machines"] == 5


@pytest.mark.parametrize(
    "kwargs",
    [
        {"resource": "unknown", "units": 1},
        {"resource": "concurrent_diagnostics", "units": 0},
        {"resource": "concurrent_diagnostics", "units": -1},
        {"resource": "concurrent_diagnostics", "units": True},
        {"resource": "concurrent_diagnostics", "units": 1.5},
    ],
)
def test_invalid_reservations_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        make_coordinator().reserve(**kwargs)


def test_non_string_reservation_id_is_rejected():
    coordinator = make_coordinator()

    with pytest.raises(TypeError):
        coordinator.complete(None)


def test_projection_is_detached_from_internal_state():
    coordinator = make_coordinator()
    coordinator.reserve()

    first = coordinator.projection()
    first["active_reservations"].clear()
    first["history"].clear()
    first["limits"]["max_concurrent_diagnostics"] = 999

    second = coordinator.projection()

    assert len(second["active_reservations"]) == 1
    assert len(second["history"]) == 1
    assert second["limits"]["max_concurrent_diagnostics"] == 3


def test_concurrent_requests_cannot_exceed_capacity():
    limit = 5
    coordinator = make_coordinator(limit=limit)

    def attempt_reservation(_):
        return coordinator.reserve()

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(attempt_reservation, range(50)))

    admitted = [result for result in results if result.admitted]
    rejected = [result for result in results if not result.admitted]

    assert len(admitted) == limit
    assert len(rejected) == 50 - limit

    snapshot = coordinator.projection()

    assert snapshot["active_reservation_count"] == limit
    assert snapshot["active_units_by_resource"]["concurrent_diagnostics"] == limit
    assert snapshot["available_capacity_by_resource"]["concurrent_diagnostics"] == 0


def test_zero_remaining_capacity_becomes_available_after_release():
    coordinator = make_coordinator(limit=1)
    first = coordinator.reserve()

    rejected = coordinator.reserve()
    assert rejected.admitted is False

    assert coordinator.release(first.reservation_id) is True

    second = coordinator.reserve()
    assert second.admitted is True


def test_capacity_evaluation_does_not_execute_work():
    coordinator = make_coordinator()

    coordinator.reserve()
    snapshot = coordinator.projection()

    assert snapshot["execution_performed"] is False

def test_coordinator_history_is_bounded():
    coordinator = BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=10,
            max_managed_machines=10,
            max_events_retained=10,
            max_projection_items=10,
        ),
        history_capacity=3,
    )

    for _ in range(5):
        result = coordinator.reserve()
        assert result.admitted is True
        assert coordinator.complete(result.reservation_id) is True

    snapshot = coordinator.projection()

    assert len(snapshot["history"]) == 3
    assert snapshot["history_capacity"] == 3
    assert snapshot["history_evicted_count"] == 7


def test_history_eviction_never_removes_active_reservations():
    coordinator = BoundedExecutionCoordinator(
        PerformanceLimits(
            max_concurrent_diagnostics=10,
            max_managed_machines=10,
            max_events_retained=10,
            max_projection_items=10,
        ),
        history_capacity=2,
    )

    active = coordinator.reserve()
    assert active.admitted is True

    for _ in range(4):
        result = coordinator.reserve()
        assert result.admitted is True
        assert coordinator.complete(result.reservation_id) is True

    snapshot = coordinator.projection()

    assert len(snapshot["history"]) == 2
    assert snapshot["history_evicted_count"] > 0
    assert len(snapshot["active_reservations"]) == 1
    assert snapshot["active_reservations"][0]["reservation_id"] == (
        active.reservation_id
    )


def test_invalid_coordinator_history_capacity_is_rejected():
    with pytest.raises(ValueError):
        BoundedExecutionCoordinator(history_capacity=0)

    with pytest.raises(TypeError):
        BoundedExecutionCoordinator(history_capacity=True)
