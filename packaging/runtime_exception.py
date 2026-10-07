"""Runtime exception containment boundary."""

from dataclasses import dataclass
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RuntimeFailure:
    error_type: str
    message: str
    operation: str

    def __post_init__(self):
        if not self.error_type.strip():
            raise ValueError("error_type must be non-empty.")

        if not self.message.strip():
            raise ValueError("message must be non-empty.")

        if not self.operation.strip():
            raise ValueError("operation must be non-empty.")


@dataclass(frozen=True)
class RuntimeResult:
    succeeded: bool
    value: object | None = None
    failure: RuntimeFailure | None = None

    def __post_init__(self):
        if self.succeeded and self.failure is not None:
            raise ValueError(
                "Successful runtime result cannot contain a failure."
            )

        if not self.succeeded and self.failure is None:
            raise ValueError(
                "Failed runtime result must contain a failure."
            )


def execute_runtime_operation(
    operation: str,
    operation_callable: Callable[[], T],
) -> RuntimeResult:
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string.")

    if not callable(operation_callable):
        raise TypeError(
            "operation_callable must be callable."
        )

    try:
        value = operation_callable()
    except Exception as exc:
        return RuntimeResult(
            succeeded=False,
            failure=RuntimeFailure(
                error_type=type(exc).__name__,
                message=str(exc) or "Runtime operation failed.",
                operation=operation,
            ),
        )

    return RuntimeResult(
        succeeded=True,
        value=value,
    )
