"""Windows Technician production resource boundary."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def resource_root() -> Path:
    """Return the canonical application resource directory."""
    return RESOURCE_ROOT


def resource_path(*parts: str) -> Path:
    """
    Resolve a resource beneath the canonical resource directory.

    Resource paths must remain inside RESOURCE_ROOT.
    """
    if not parts:
        raise ValueError("At least one resource path component is required.")

    candidate = RESOURCE_ROOT.joinpath(*parts).resolve()

    try:
        candidate.relative_to(RESOURCE_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            "Resource path escapes the application resource boundary."
        ) from exc

    return candidate


def resource_exists(*parts: str) -> bool:
    """Return whether a resource exists inside the resource boundary."""
    return resource_path(*parts).exists()
