"""Windows Technician production runtime configuration boundary."""

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class RuntimePaths:
    """Canonical runtime filesystem locations."""

    application_data: Path
    configuration: Path
    logs: Path
    reports: Path

    def ensure(self) -> None:
        """Create runtime directories when they do not exist."""
        for path in (
            self.application_data,
            self.configuration,
            self.logs,
            self.reports,
        ):
            path.mkdir(parents=True, exist_ok=True)


def default_runtime_paths() -> RuntimePaths:
    """
    Return Windows-safe per-user runtime locations.

    The application does not write runtime state into its installation
    directory by default.
    """
    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        root = Path(local_app_data) / "WindowsTechnician"
    else:
        root = Path.home() / "AppData" / "Local" / "WindowsTechnician"

    return RuntimePaths(
        application_data=root,
        configuration=root / "config",
        logs=root / "logs",
        reports=root / "reports",
    )


def initialize_runtime_paths(
    paths: RuntimePaths | None = None,
) -> RuntimePaths:
    """Ensure runtime directories exist and return the active paths."""
    active_paths = paths or default_runtime_paths()
    active_paths.ensure()
    return active_paths
