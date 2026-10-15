"""Explicit trace and correlation context for Windows Technician V1.0."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


def _validate_identifier(value: str | None, name: str) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string or None.")

    if not value.strip():
        raise ValueError(f"{name} cannot be blank.")

    return value.strip()


def _new_identifier() -> str:
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class ObservabilityContext:
    """Immutable identifiers connecting related diagnostic operations.

    A context is explicitly passed between components. It does not install
    global state, initiate operations, or transmit telemetry.
    """

    trace_id: str
    correlation_id: str
    case_id: str | None = None
    operation_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "trace_id",
            "correlation_id",
            "case_id",
            "operation_id",
        ):
            value = _validate_identifier(getattr(self, name), name)

            if name in ("trace_id", "correlation_id") and value is None:
                raise ValueError(f"{name} is required.")

            object.__setattr__(self, name, value)

    @classmethod
    def create(
        cls,
        *,
        case_id: str | None = None,
        operation_id: str | None = None,
        trace_id: str | None = None,
        correlation_id: str | None = None,
    ) -> "ObservabilityContext":
        """Create an independent context, generating missing identifiers."""
        return cls(
            trace_id=trace_id or _new_identifier(),
            correlation_id=correlation_id or _new_identifier(),
            case_id=case_id,
            operation_id=operation_id,
        )

    def child(
        self,
        *,
        case_id: str | None = None,
        operation_id: str | None = None,
    ) -> "ObservabilityContext":
        """Create a related context preserving the trace and correlation IDs.

        Omitted identifiers inherit from the parent. An explicit non-None
        identifier replaces the corresponding parent identifier.
        """
        return ObservabilityContext(
            trace_id=self.trace_id,
            correlation_id=self.correlation_id,
            case_id=self.case_id if case_id is None else case_id,
            operation_id=(
                self.operation_id
                if operation_id is None
                else operation_id
            ),
        )

    def projection(self) -> dict[str, str | None]:
        """Return a detached serialization-friendly identifier snapshot."""
        return {
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "case_id": self.case_id,
            "operation_id": self.operation_id,
        }
