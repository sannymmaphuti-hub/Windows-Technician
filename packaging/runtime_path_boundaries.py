"""Filesystem boundaries for source and packaged application execution."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ApplicationPaths:
    """Resolved application, resource, and writable-data directories."""

    application_root: Path
    resource_root: Path
    user_data_root: Path


def resolve_application_paths(
    app_name: str,
    module_file: str | Path,
    *,
    is_frozen: bool | None = None,
    executable: str | Path | None = None,
    bundle_dir: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    home: str | Path | None = None,
) -> ApplicationPaths:
    """Resolve paths without creating directories or changing system state.

    Source execution uses the source directory for application resources.

    Frozen execution separates the executable's installation directory from
    the bundle's resource directory.

    Writable data prefers LOCALAPPDATA, then APPDATA, then a home fallback.
    """
    if not isinstance(app_name, str) or not app_name.strip():
        raise ValueError("app_name must be a non-empty string.")

    if not isinstance(module_file, (str, Path)):
        raise TypeError("module_file must be a path.")

    frozen = (
        bool(getattr(sys, "frozen", False))
        if is_frozen is None
        else is_frozen
    )

    if not isinstance(frozen, bool):
        raise TypeError("is_frozen must be a boolean or None.")

    environment = os.environ if environ is None else environ
    source_root = Path(module_file).expanduser().resolve().parent

    if frozen:
        executable_path = Path(
            executable if executable is not None else sys.executable
        ).expanduser().resolve()

        application_root = executable_path.parent

        resolved_bundle = bundle_dir
        if resolved_bundle is None:
            resolved_bundle = getattr(sys, "_MEIPASS", source_root)

        resource_root = Path(resolved_bundle).expanduser().resolve()
    else:
        application_root = source_root
        resource_root = source_root

    local_app_data = environment.get("LOCALAPPDATA", "").strip()
    roaming_app_data = environment.get("APPDATA", "").strip()

    if local_app_data:
        data_base = Path(local_app_data).expanduser()
    elif roaming_app_data:
        data_base = Path(roaming_app_data).expanduser()
    else:
        home_path = Path(home).expanduser() if home is not None else Path.home()
        data_base = home_path / ".local" / "share"

    return ApplicationPaths(
        application_root=application_root,
        resource_root=resource_root,
        user_data_root=(data_base / app_name).resolve(),
    )
