"""Structured observability event model for Windows Technician V1.0."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any
from uuid import uuid4


class ObservabilitySeverity(str, Enum):
    """Severity classification for structured application events."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _freeze_value(value: Any) -> Any:
    """Convert supported metadata values into immutable representations."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Mapping):
        frozen = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Attribute mapping keys must be non-empty strings.")
            frozen[key] = _freeze_value(item)
        return MappingProxyType(frozen)

    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)

    raise TypeError(
        "Event attributes must contain only scalar values, mappings, "
        "lists, or tuples."
    )


@dataclass(frozen=True, slots=True)
class StructuredObservabilityEvent:
    """Immutable, local structured event; it does not transmit telemetry."""

    event_type: str
    severity: ObservabilitySeverity = ObservabilitySeverity.INFO
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    case_id: str | None = None
    operation_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "event_type",
            _require_non_empty_string(self.event_type, "event_type"),
        )
        object.__setattr__(
            self,
            "event_id",
            _require_non_empty_string(self.event_id, "event_id"),
        )

        if not isinstance(self.severity, ObservabilitySeverity):
            try:
                object.__setattr__(
                    self,
                    "severity",
                    ObservabilitySeverity(self.severity),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError("severity must be a valid observability severity.") from exc

        if not isinstance(self.occurred_at, datetime):
            raise TypeError("occurred_at must be a datetime.")

        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware.")

        object.__setattr__(
            self,
            "occurred_at",
            self.occurred_at.astimezone(timezone.utc),
        )

        for name in ("case_id", "operation_id", "correlation_id", "trace_id"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(
                    self,
                    name,
                    _require_non_empty_string(value, name),
                )

        if not isinstance(self.attributes, Mapping):
            raise TypeError("attributes must be a mapping.")

        frozen_attributes = {}
        for key, value in self.attributes.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Attribute keys must be non-empty strings.")
            frozen_attributes[key] = _freeze_value(value)

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(frozen_attributes),
        )

    def projection(self) -> dict[str, Any]:
        """Return a detached, serialization-friendly event representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "occurred_at": self.occurred_at.isoformat(),
            "case_id": self.case_id,
            "operation_id": self.operation_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "attributes": _thaw_value(self.attributes),
        }


def _thaw_value(value: Any) -> Any:
    """Create detached built-in containers for a public projection."""
    if isinstance(value, Mapping):
        return {key: _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value
