"""Read-only observability boundary for Windows Technician V1.0."""

from collections.abc import Mapping


class ObservabilityBoundary:
    """Expose existing engine and reliability state without changing it.

    This boundary is a projection layer only. It does not execute operations,
    authorize remediation, or introduce a competing lifecycle.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        problem_solving_engine=None,
        reliability_service=None,
        *,
        telemetry_enabled=False,
    ):
        if not isinstance(telemetry_enabled, bool):
            raise TypeError("telemetry_enabled must be a boolean.")

        self._problem_solving_engine = problem_solving_engine
        self._reliability_service = reliability_service
        self._telemetry_enabled = telemetry_enabled

        self._validate_projection_provider(
            problem_solving_engine,
            "problem_solving_engine",
        )
        self._validate_projection_provider(
            reliability_service,
            "reliability_service",
        )

    @staticmethod
    def _validate_projection_provider(provider, name):
        if provider is None:
            return

        projection = getattr(provider, "projection", None)

        if not callable(projection):
            raise TypeError(
                f"{name} must provide a callable projection() method."
            )

    @property
    def telemetry_enabled(self):
        """Return whether telemetry was explicitly enabled."""
        return self._telemetry_enabled

    def projection(self):
        """Return a snapshot of existing subsystem projections.

        Calling this method does not initiate diagnostics, remediation,
        retries, recovery, or telemetry transmission.
        """
        engine_projection = self._read_projection(
            self._problem_solving_engine,
            "problem_solving_engine",
        )
        reliability_projection = self._read_projection(
            self._reliability_service,
            "reliability_service",
        )

        return {
            "schema_version": self.SCHEMA_VERSION,
            "telemetry_enabled": self._telemetry_enabled,
            "engine": engine_projection,
            "reliability": reliability_projection,
        }

    @staticmethod
    def _read_projection(provider, name):
        if provider is None:
            return None

        result = provider.projection()

        if not isinstance(result, Mapping):
            raise TypeError(
                f"{name}.projection() must return a mapping."
            )

        # Copy the outer mapping so callers cannot modify the dictionary
        # returned directly by the subsystem's projection method.
        return dict(result)
