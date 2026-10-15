from engine.security_audit_event import SecurityAuditEvent


class SecurityAuditHistory:
    """Append-only in-memory history of security audit events."""

    def __init__(self):
        self._events = []
        self._event_ids = set()

    @property
    def event_count(self):
        return len(self._events)

    @property
    def events(self):
        return tuple(self.chronological_events())

    def append(self, event):
        if not isinstance(event, SecurityAuditEvent):
            raise TypeError("event must be a SecurityAuditEvent.")

        if event.event_id in self._event_ids:
            raise ValueError(
                f"Duplicate security audit event ID: {event.event_id}"
            )

        self._events.append(event)
        self._event_ids.add(event.event_id)
        return event.event_id

    def chronological_events(self):
        return sorted(
            self._events,
            key=lambda event: (event.occurred_at, event.event_id),
        )

    def projection(self):
        events = [
            event.projection()
            for event in self.chronological_events()
        ]

        return {
            "event_count": len(events),
            "events": events,
        }

    def __repr__(self):
        return f"SecurityAuditHistory(event_count={self.event_count})"
