from dataclasses import FrozenInstanceError
from datetime import timezone

import pytest

from engine.security_audit_event import (
    SecurityAuditEventFactory,
)


def create_event(**overrides):
    values = {
        "event_type": "CASE_ACCESS",
        "actor_id": "TECH-001",
        "resource_id": "CASE-001",
        "action": "VIEW_CASE",
        "outcome": "ALLOWED",
        "reason": "CASE_ACCESS_GRANTED",
    }
    values.update(overrides)
    return SecurityAuditEventFactory().create(**values)


def test_factory_creates_a_unique_event():
    first = create_event()
    second = create_event()

    assert first.event_id
    assert first.event_id != second.event_id


def test_event_records_security_context():
    event = create_event()

    assert event.event_type == "CASE_ACCESS"
    assert event.actor_id == "TECH-001"
    assert event.resource_id == "CASE-001"
    assert event.action == "VIEW_CASE"
    assert event.outcome == "ALLOWED"
    assert event.reason == "CASE_ACCESS_GRANTED"


def test_event_timestamp_is_timezone_aware():
    event = create_event()

    assert event.occurred_at.tzinfo is not None
    assert event.occurred_at.utcoffset().total_seconds() == 0
    assert event.occurred_at.tzinfo == timezone.utc


def test_event_is_immutable():
    event = create_event()

    with pytest.raises(FrozenInstanceError):
        event.outcome = "DENIED"


def test_projection_is_serializable():
    event = create_event()
    projection = event.projection()

    assert projection["event_id"] == event.event_id
    assert projection["occurred_at"].endswith("+00:00")


def test_projection_mutation_does_not_change_event():
    event = create_event()
    projection = event.projection()
    projection["outcome"] = "DENIED"

    assert event.outcome == "ALLOWED"
    assert event.projection()["outcome"] == "ALLOWED"


def test_invalid_required_fields_are_rejected():
    for field in (
        "event_type",
        "actor_id",
        "resource_id",
        "action",
        "outcome",
        "reason",
    ):
        with pytest.raises(ValueError):
            create_event(**{field: "   "})


def test_unsupported_outcome_is_rejected():
    with pytest.raises(ValueError, match="Unsupported security audit outcome"):
        create_event(outcome="MAYBE")


def test_event_normalizes_event_type_action_and_outcome():
    event = create_event(
        event_type=" case_access ",
        action=" view_case ",
        outcome="allowed",
    )

    assert event.event_type == "CASE_ACCESS"
    assert event.action == "VIEW_CASE"
    assert event.outcome == "ALLOWED"


def test_repr_does_not_expose_actor_or_resource_ids():
    event = create_event()

    assert "TECH-001" not in repr(event)
    assert "CASE-001" not in repr(event)
