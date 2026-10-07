"""Structured runtime logging boundary."""

from dataclasses import dataclass
import logging


@dataclass(frozen=True)
class LogEvent:
    level: int
    event: str
    component: str
    message: str

    def __post_init__(self):
        if not isinstance(self.level, int):
            raise TypeError("level must be an integer.")

        for field_name, value in (
            ("event", self.event),
            ("component", self.component),
            ("message", self.message),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )


def create_log_event(
    *,
    level: int,
    event: str,
    component: str,
    message: str,
) -> LogEvent:
    return LogEvent(
        level=level,
        event=event,
        component=component,
        message=message,
    )


def emit_log_event(
    logger: logging.Logger,
    event: LogEvent,
) -> None:
    if not isinstance(logger, logging.Logger):
        raise TypeError(
            "logger must be a logging.Logger."
        )

    if not isinstance(event, LogEvent):
        raise TypeError(
            "event must be a LogEvent."
        )

    logger.log(
        event.level,
        "[%s] %s",
        event.event,
        event.message,
        extra={
            "wt_event": event.event,
            "wt_component": event.component,
        },
    )
