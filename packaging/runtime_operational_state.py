"""Operational-state integration for the production application runtime."""

from packaging.operational_state import (
    OperationalState,
    OperationalStateStore,
    operational_state_path,
)
from packaging.runtime_configuration import (
    RuntimePaths,
    initialize_runtime_paths,
)


class RuntimeOperationalState:
    """
    Coordinates durable operational state for an application runtime.

    This is deliberately separate from configuration. Configuration
    describes how the application should operate; operational state
    describes what happened during the previous runtime session.
    """

    def __init__(self, store: OperationalStateStore):
        if not isinstance(store, OperationalStateStore):
            raise TypeError(
                "store must be an OperationalStateStore."
            )

        self.store = store

    @classmethod
    def from_runtime_paths(cls, runtime_paths: RuntimePaths):
        if not isinstance(runtime_paths, RuntimePaths):
            raise TypeError(
                "runtime_paths must be RuntimePaths."
            )

        paths = initialize_runtime_paths(runtime_paths)

        return cls(
            OperationalStateStore(
                operational_state_path(paths)
            )
        )

    def persist(
        self,
        *,
        lifecycle_state: str,
        clean_shutdown: bool,
        recovered: bool = False,
    ) -> OperationalState:
        state = OperationalState(
            lifecycle_state=lifecycle_state,
            clean_shutdown=clean_shutdown,
            recovered=recovered,
        )

        self.store.save(state)

        return state

    def recover(self) -> OperationalState:
        return self.store.recover()
