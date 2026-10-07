"""Runtime dependency availability boundary."""

from dataclasses import dataclass
import importlib


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    available: bool
    error_type: str | None = None
    message: str | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string.")

        if self.available and (
            self.error_type is not None
            or self.message is not None
        ):
            raise ValueError(
                "Available dependency cannot contain failure details."
            )

        if not self.available and not self.error_type:
            raise ValueError(
                "Unavailable dependency must contain error_type."
            )


def check_dependency(name: str) -> DependencyStatus:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string.")

    try:
        importlib.import_module(name)
    except Exception as exc:
        return DependencyStatus(
            name=name,
            available=False,
            error_type=type(exc).__name__,
            message=str(exc) or "Dependency could not be loaded.",
        )

    return DependencyStatus(
        name=name,
        available=True,
    )


def check_dependencies(
    names: tuple[str, ...],
) -> tuple[DependencyStatus, ...]:
    if not isinstance(names, tuple):
        raise TypeError("names must be a tuple.")

    return tuple(
        check_dependency(name)
        for name in names
    )


def all_dependencies_available(
    statuses: tuple[DependencyStatus, ...],
) -> bool:
    if not isinstance(statuses, tuple):
        raise TypeError("statuses must be a tuple.")

    return all(
        status.available
        for status in statuses
    )
