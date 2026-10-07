"""Persistent operational state for the Windows Technician runtime."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class OperationalState:
    """Small durable record describing the previous runtime session."""

    schema_version: int = 1
    lifecycle_state: str = "CREATED"
    clean_shutdown: bool = False
    recovered: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.schema_version, int):
            raise TypeError("schema_version must be an integer.")

        if self.schema_version <= 0:
            raise ValueError("schema_version must be positive.")

        if not isinstance(self.lifecycle_state, str):
            raise TypeError("lifecycle_state must be a string.")

        if not self.lifecycle_state.strip():
            raise ValueError("lifecycle_state must be non-empty.")

        if not isinstance(self.clean_shutdown, bool):
            raise TypeError("clean_shutdown must be a boolean.")

        if not isinstance(self.recovered, bool):
            raise TypeError("recovered must be a boolean.")


class OperationalStateStore:
    """Persists and restores operational runtime state."""

    def __init__(self, path: Path):
        if not isinstance(path, Path):
            raise TypeError("path must be a Path.")

        self.path = path

    def save(self, state: OperationalState) -> None:
        if not isinstance(state, OperationalState):
            raise TypeError("state must be an OperationalState.")

        self.path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                asdict(state),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(self.path)

    def load(self) -> OperationalState | None:
        if not self.path.exists():
            return None

        if not self.path.is_file():
            raise ValueError("operational state path must be a file.")

        try:
            payload = json.loads(
                self.path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                "operational state could not be loaded."
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "operational state must contain an object."
            )

        try:
            return OperationalState(**payload)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "operational state is invalid."
            ) from exc

    def recover(self) -> OperationalState:
        """
        Recover the previous operational state.

        Missing state means a fresh runtime. An unclean previous session
        is explicitly marked as recovered.
        """
        previous = self.load()

        if previous is None:
            return OperationalState(
                lifecycle_state="CREATED",
                clean_shutdown=False,
                recovered=False,
            )

        return OperationalState(
            schema_version=previous.schema_version,
            lifecycle_state=previous.lifecycle_state,
            clean_shutdown=previous.clean_shutdown,
            recovered=(
                not previous.clean_shutdown
                or previous.recovered
            ),
        )


def operational_state_path(runtime_paths) -> Path:
    """Return the canonical operational-state path."""
    return runtime_paths.application_data / "operational_state.json"
