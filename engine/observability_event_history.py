"""Bounded, thread-safe observability event history for Windows Technician."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any

from engine.structured_observability_event import (
    ObservabilitySeverity,
    StructuredObservabilityEvent,
)


class ObservabilityEventHistory:
    """Record and query structured events in bounded in-memory history.

    This component does not persist events, transmit telemetry, execute
    operations, or replace diagnostic/security audit history.
    """

    DEFAULT_CAPACITY = 1000

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer.")

        if capacity < 1:
            raise ValueError("capacity must be at least 1.")

        self._capacity = capacity
        self._events: list[StructuredObservabilityEvent] = []
        self._event_ids: set[str] = set()
        self._lock = RLock()
        self._evicted_count = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)

    def record(
        self,
        event: StructuredObservabilityEvent,
    ) -> dict[str, Any]:
        """Record one event and return its detached projection."""
        if not isinstance(event, StructuredObservabilityEvent):
            raise TypeError(
                "event must be a StructuredObservabilityEvent."
            )

        with self._lock:
            if event.event_id in self._event_ids:
                raise ValueError(
                    f"Duplicate observability event ID: {event.event_id}"
                )

            self._events.append(event)
            self._event_ids.add(event.event_id)

            if len(self._events) > self._capacity:
                evicted = self._events.pop(0)
                self._event_ids.remove(evicted.event_id)
                self._evicted_count += 1

            return event.projection()

    def query(
        self,
        *,
        event_type: str | None = None,
        severity: ObservabilitySeverity | str | None = None,
        case_id: str | None = None,
        operation_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return detached projections matching all supplied filters."""
        filters = {
            "event_type": event_type,
            "case_id": case_id,
            "operation_id": operation_id,
            "correlation_id": correlation_id,
            "trace_id": trace_id,
        }

        for name, value in filters.items():
            if value is not None:
                if not isinstance(value, str):
                    raise TypeError(f"{name} must be a string or None.")
                if not value.strip():
                    raise ValueError(f"{name} cannot be blank.")

        normalized_severity = None
        if severity is not None:
            try:
                normalized_severity = ObservabilitySeverity(severity).value
            except (ValueError, TypeError) as exc:
                raise ValueError("Invalid observability severity.") from exc

        for name, value in (("since", since), ("until", until)):
            if value is not None:
                if not isinstance(value, datetime):
                    raise TypeError(f"{name} must be a datetime or None.")
                if value.tzinfo is None or value.utcoffset() is None:
                    raise ValueError(f"{name} must be timezone-aware.")

        lower = since.astimezone(timezone.utc) if since else None
        upper = until.astimezone(timezone.utc) if until else None

        if lower is not None and upper is not None and lower > upper:
            raise ValueError("since cannot be later than until.")

        if limit is not None:
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise TypeError("limit must be an integer or None.")
            if limit < 0:
                raise ValueError("limit cannot be negative.")

        with self._lock:
            matched = []

            for event in self._events:
                if event_type is not None and event.event_type != event_type:
                    continue

                if (
                    normalized_severity is not None
                    and event.severity.value != normalized_severity
                ):
                    continue

                if case_id is not None and event.case_id != case_id:
                    continue

                if (
                    operation_id is not None
                    and event.operation_id != operation_id
                ):
                    continue

                if (
                    correlation_id is not None
                    and event.correlation_id != correlation_id
                ):
                    continue

                if trace_id is not None and event.trace_id != trace_id:
                    continue

                occurred_at = event.occurred_at

                if lower is not None and occurred_at < lower:
                    continue

                if upper is not None and occurred_at > upper:
                    continue

                matched.append(event.projection())

            if limit is not None:
                matched = matched[:limit]

            return matched

    def projection(self) -> dict[str, Any]:
        """Return a detached summary of the current retained history."""
        with self._lock:
            return {
                "capacity": self._capacity,
                "event_count": len(self._events),
                "evicted_event_count": self._evicted_count,
                "events": [
                    event.projection()
                    for event in self._events
                ],
            }
