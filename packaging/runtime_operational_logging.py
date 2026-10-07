"""Operational lifecycle logging boundary for the production runtime."""

from engine.application_logging import ApplicationLogger


class RuntimeOperationalLogger:
    """
    Records production runtime lifecycle events.

    This boundary records what the runtime did. It does not perform
    diagnostics, remediation, authorization, recovery decisions, or
    execution.
    """

    COMPONENT = "ApplicationRuntime"

    def __init__(self, logger: ApplicationLogger):
        if not isinstance(logger, ApplicationLogger):
            raise TypeError(
                "logger must be an ApplicationLogger."
            )

        self.logger = logger

    def log_event(
        self,
        event: str,
        message: str,
        *,
        level: str = "INFO",
    ) -> str:
        if not isinstance(event, str) or not event.strip():
            raise ValueError(
                "event must be a non-empty string."
            )

        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "message must be a non-empty string."
            )

        normalized_event = event.strip().upper()
        normalized_message = message.strip()

        return self.logger.log(
            level,
            f"[{self.COMPONENT}] "
            f"[{normalized_event}] "
            f"{normalized_message}",
        )

    def application_starting(self) -> str:
        return self.log_event(
            "APPLICATION_STARTING",
            "Application runtime startup has begun.",
        )

    def application_running(self) -> str:
        return self.log_event(
            "APPLICATION_RUNNING",
            "Application runtime is running.",
        )

    def application_recovery(self) -> str:
        return self.log_event(
            "APPLICATION_RECOVERY",
            "Previous application session requires recovery.",
            level="WARNING",
        )

    def application_degraded(self) -> str:
        return self.log_event(
            "APPLICATION_DEGRADED",
            "Application runtime entered a degraded state.",
            level="WARNING",
        )

    def application_failed(self, message: str) -> str:
        return self.log_event(
            "APPLICATION_FAILED",
            message,
            level="ERROR",
        )

    def application_stopping(self) -> str:
        return self.log_event(
            "APPLICATION_STOPPING",
            "Application runtime shutdown has begun.",
        )

    def application_stopped(self) -> str:
        return self.log_event(
            "APPLICATION_STOPPED",
            "Application runtime stopped cleanly.",
        )
