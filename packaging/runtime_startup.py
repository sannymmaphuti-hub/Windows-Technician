"""Runtime startup reliability boundary."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class StartupFailure:
    error_type: str
    message: str

    def __post_init__(self):
        if not self.error_type.strip():
            raise ValueError("error_type must be non-empty.")

        if not self.message.strip():
            raise ValueError("message must be non-empty.")


@dataclass(frozen=True)
class StartupResult:
    succeeded: bool
    failure: StartupFailure | None = None

    def __post_init__(self):
        if self.succeeded and self.failure is not None:
            raise ValueError(
                "Successful startup cannot contain a failure."
            )

        if not self.succeeded and self.failure is None:
            raise ValueError(
                "Failed startup must contain a failure."
            )


def execute_startup(
    startup_callable: Callable[[], None],
) -> StartupResult:
    if not callable(startup_callable):
        raise TypeError(
            "startup_callable must be callable."
        )

    try:
        startup_callable()
    except Exception as exc:
        return StartupResult(
            succeeded=False,
            failure=StartupFailure(
                error_type=type(exc).__name__,
                message=str(exc) or "Startup failed.",
            ),
        )

    return StartupResult(succeeded=True)
