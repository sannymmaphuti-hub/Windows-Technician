from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class SecurityAuditEvent:
    """Immutable record of a security-relevant event."""

    event_id: str
    event_type: str
    actor_id: str
    resource_id: str
    action: str
    outcome: str
    reason: str
    occurred_at: datetime

    def projection(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "resource_id": self.resource_id,
            "action": self.action,
            "outcome": self.outcome,
            "reason": self.reason,
            "occurred_at": self.occurred_at.isoformat(),
        }

    def __repr__(self):
        return (
            "SecurityAuditEvent("
            f"event_type={self.event_type!r}, "
            f"outcome={self.outcome!r})"
        )


class SecurityAuditEventFactory:
    """Creates validated security audit events."""

    VALID_OUTCOMES = {"ALLOWED", "DENIED", "INFO"}

    def create(
        self,
        event_type,
        actor_id,
        resource_id,
        action,
        outcome,
        reason,
    ):
        values = {
            "event_type": event_type,
            "actor_id": actor_id,
            "resource_id": resource_id,
            "action": action,
            "outcome": outcome,
            "reason": reason,
        }

        for name, value in values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")

        normalized_outcome = outcome.strip().upper()

        if normalized_outcome not in self.VALID_OUTCOMES:
            raise ValueError(
                f"Unsupported security audit outcome: {outcome!r}"
            )

        return SecurityAuditEvent(
            event_id=str(uuid4()),
            event_type=event_type.strip().upper(),
            actor_id=actor_id.strip(),
            resource_id=resource_id.strip(),
            action=action.strip().upper(),
            outcome=normalized_outcome,
            reason=reason.strip().upper(),
            occurred_at=datetime.now(timezone.utc),
        )
