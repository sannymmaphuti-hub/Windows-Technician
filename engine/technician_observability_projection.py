"""Technician-facing observability projection for Windows Technician V1.0."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any


class TechnicianObservabilityProjection:
    """Combine existing observability projections into one snapshot.

    All inputs are read-only providers. This class does not create a competing
    operation lifecycle, authorize actions, or execute recovery.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        *,
        observability_boundary=None,
        operation_metrics=None,
        reliability_metrics=None,
        event_history=None,
    ) -> None:
        providers = {
            "observability_boundary": observability_boundary,
            "operation_metrics": operation_metrics,
            "reliability_metrics": reliability_metrics,
            "event_history": event_history,
        }

        for name, provider in providers.items():
            if provider is not None and not callable(
                getattr(provider, "projection", None)
            ):
                raise TypeError(f"{name} must provide projection().")

        self._observability_boundary = observability_boundary
        self._operation_metrics = operation_metrics
        self._reliability_metrics = reliability_metrics
        self._event_history = event_history

    @staticmethod
    def _read_provider(provider, name: str) -> dict[str, Any] | None:
        if provider is None:
            return None

        result = provider.projection()

        if not isinstance(result, Mapping):
            raise TypeError(f"{name}.projection() must return a mapping.")

        # Provider projections are expected to be detached mappings.
        # Copy the outer mapping so this combined projection never returns
        # the provider's top-level dictionary directly.
        return deepcopy(dict(result))

    def projection(self) -> dict[str, Any]:
        """Return one timestamped snapshot of the available projections."""
        boundary = self._read_provider(
            self._observability_boundary,
            "observability_boundary",
        )
        operation_metrics = self._read_provider(
            self._operation_metrics,
            "operation_metrics",
        )
        reliability_metrics = self._read_provider(
            self._reliability_metrics,
            "reliability_metrics",
        )
        event_history = self._read_provider(
            self._event_history,
            "event_history",
        )

        event_summary = None
        if event_history is not None:
            event_summary = {
                "capacity": event_history.get("capacity"),
                "event_count": event_history.get("event_count"),
                "evicted_event_count": event_history.get(
                    "evicted_event_count"
                ),
            }

        return {
            "schema_version": self.SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "observability": boundary,
            "operation_metrics": operation_metrics,
            "reliability_metrics": reliability_metrics,
            "event_history": event_summary,
        }
