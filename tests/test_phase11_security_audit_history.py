from dataclasses import FrozenInstanceError
from datetime import datetime, timezone, timedelta

import pytest

from engine.security_audit_event import (
    SecurityAuditEvent,
    SecurityAuditEventFactory,
)
from engine.security_audit_history import SecurityAuditHistory


def create_event():
    return SecurityAuditEventFactory().create(
        event_type="CASE_ACCESS",
        actor_id="TECH-001",
        resource_id="CASE-001",
        action="VIEW_CASE",
        outcome="ALLOWED",
        reason="CASE_ACCESS_GRANTED",
    )


def test_history_starts_empty():
    history = SecurityAuditHistory()

    assert history.event_count == 0
    assert history.events == ()
    assert history.projection() == {
        "event_count": 0,
        "events": [],
    }


def test_history_appends_valid_event():
    history = SecurityAuditHistory()
    event = create_event()

    assert history.append(event) == event.event_id
    assert history.event_count == 1
    assert history.events == (event,)


def test_history_rejects_invalid_event():
    history = SecurityAuditHistory()

    with pytest.raises(TypeError):
        history.append({"event_type": "CASE_ACCESS"})


def test_history_rejects_duplicate_event_id():
    history = SecurityAuditHistory()
    event = create_event()

    history.append(event)

    with pytest.raises(ValueError, match="Duplicate security audit event ID"):
        history.append(event)


def test_events_property_returns_immutable_container():
    history = SecurityAuditHistory()
    history.append(create_event())

    assert isinstance(history.events, tuple)


def test_history_returns_events_chronologically():
    history = SecurityAuditHistory()
    now = datetime.now(timezone.utc)

    later = SecurityAuditEvent(
        event_id="EVENT-LATER",
        event_type="CASE_ACCESS",
        actor_id="TECH-001",
        resource_id="CASE-001",
        action="VIEW_CASE",
        outcome="ALLOWED",
        reason="GRANTED",
        occurred_at=now + timedelta(minutes=2),
    )

    earlier = SecurityAuditEvent(
        event_id="EVENT-EARLIER",
        event_type="CASE_ACCESS",
        actor_id="TECH-001",
        resource_id="CASE-001",
        action="VIEW_CASE",
        outcome="DENIED",
        reason="DENIED",
        occurred_at=now,
    )

    history.append(later)
    history.append(earlier)

    assert [
        event.event_id for event in history.chronological_events()
    ] == ["EVENT-EARLIER", "EVENT-LATER"]


def test_projection_mutation_does_not_change_history():
    history = SecurityAuditHistory()
    history.append(create_event())

    projection = history.projection()
    projection["events"].clear()
    projection["event_count"] = 0

    assert history.event_count == 1
    assert history.projection()["event_count"] == 1


def test_history_does_not_mutate_stored_events():
    history = SecurityAuditHistory()
    event = create_event()
    original_outcome = event.outcome

    history.append(event)

    with pytest.raises(FrozenInstanceError):
        event.outcome = "DENIED"

    assert history.events[0].outcome == original_outcome


def test_history_repr_reports_count_only():
    history = SecurityAuditHistory()
    history.append(create_event())

    assert repr(history) == "SecurityAuditHistory(event_count=1)"
