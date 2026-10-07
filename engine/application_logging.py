from datetime import datetime, timezone
from pathlib import Path


class ApplicationLogger:
    """
    Minimal application logging boundary.

    Logging records application events. It does not perform
    diagnostics, remediation, authorization, or execution.
    """

    _LEVELS = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    def __init__(self, log_path=None):
        self.log_path = (
            Path(log_path)
            if log_path is not None
            else None
        )

    def log(self, level, message):
        normalized_level = self._normalize_level(level)

        if not isinstance(message, str):
            raise ValueError(
                "message must be a string."
            )

        message = message.strip()

        if not message:
            raise ValueError(
                "message must be a non-empty string."
            )

        entry = self._format_entry(
            normalized_level,
            message,
        )

        if self.log_path is not None:
            self.log_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self.log_path.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(entry + "\n")

        return entry

    def debug(self, message):
        return self.log("DEBUG", message)

    def info(self, message):
        return self.log("INFO", message)

    def warning(self, message):
        return self.log("WARNING", message)

    def error(self, message):
        return self.log("ERROR", message)

    def critical(self, message):
        return self.log("CRITICAL", message)

    @classmethod
    def _normalize_level(cls, level):
        if not isinstance(level, str):
            raise ValueError(
                "level must be a supported string value."
            )

        normalized = level.strip().upper()

        if normalized not in cls._LEVELS:
            raise ValueError(
                f"Unsupported log level: {level!r}."
            )

        return normalized

    @staticmethod
    def _format_entry(level, message):
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        return (
            f"{timestamp} | "
            f"{level} | "
            f"{message}"
        )


class CrashBoundary:
    """
    Safe application exception boundary.

    Converts unexpected exceptions into structured information
    without silently executing recovery or remediation.
    """

    def __init__(self, logger=None):
        self.logger = logger

    def handle(self, exception):
        if not isinstance(exception, BaseException):
            raise ValueError(
                "CrashBoundary requires an exception."
            )

        error_type = type(exception).__name__
        message = str(exception)

        if self.logger is not None:
            self.logger.critical(
                f"Unhandled application exception: "
                f"{error_type}: {message}"
            )

        return {
            "status": "ERROR",
            "error_type": error_type,
            "message": message,
        }

    def protect(self, operation):
        if not callable(operation):
            raise ValueError(
                "Protected operation must be callable."
            )

        try:
            return {
                "status": "SUCCESS",
                "result": operation(),
            }
        except Exception as exception:
            return self.handle(exception)
