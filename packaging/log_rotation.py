"""Production log rotation and retention boundary."""

from dataclasses import dataclass
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


@dataclass(frozen=True)
class LogRotationPolicy:
    max_bytes: int
    backup_count: int

    def __post_init__(self):
        if not isinstance(self.max_bytes, int):
            raise TypeError("max_bytes must be an integer.")

        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be greater than zero.")

        if not isinstance(self.backup_count, int):
            raise TypeError("backup_count must be an integer.")

        if self.backup_count < 0:
            raise ValueError("backup_count cannot be negative.")


DEFAULT_LOG_ROTATION_POLICY = LogRotationPolicy(
    max_bytes=5 * 1024 * 1024,
    backup_count=5,
)


def create_rotating_file_handler(
    log_path: Path,
    policy: LogRotationPolicy = DEFAULT_LOG_ROTATION_POLICY,
) -> RotatingFileHandler:
    if not isinstance(log_path, Path):
        raise TypeError("log_path must be a Path.")

    if not isinstance(policy, LogRotationPolicy):
        raise TypeError(
            "policy must be a LogRotationPolicy."
        )

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return RotatingFileHandler(
        filename=log_path,
        maxBytes=policy.max_bytes,
        backupCount=policy.backup_count,
        encoding="utf-8",
    )


def configure_rotating_file_logging(
    logger: logging.Logger,
    log_path: Path,
    policy: LogRotationPolicy = DEFAULT_LOG_ROTATION_POLICY,
) -> RotatingFileHandler:
    if not isinstance(logger, logging.Logger):
        raise TypeError(
            "logger must be a logging.Logger."
        )

    handler = create_rotating_file_handler(
        log_path,
        policy,
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    logger.addHandler(handler)

    return handler
