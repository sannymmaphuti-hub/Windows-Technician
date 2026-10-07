"""Production logging architecture."""

from dataclasses import dataclass
from pathlib import Path
import logging


@dataclass(frozen=True)
class LoggingConfiguration:
    logger_name: str
    log_directory: Path
    log_filename: str
    level: int

    def __post_init__(self):
        if not self.logger_name.strip():
            raise ValueError(
                "logger_name must be non-empty."
            )

        if not isinstance(self.log_directory, Path):
            raise TypeError(
                "log_directory must be a Path."
            )

        if not self.log_filename.strip():
            raise ValueError(
                "log_filename must be non-empty."
            )

        if not isinstance(self.level, int):
            raise TypeError(
                "level must be an integer."
            )


def build_logging_configuration(
    log_directory: Path,
) -> LoggingConfiguration:
    if not isinstance(log_directory, Path):
        raise TypeError(
            "log_directory must be a Path."
        )

    return LoggingConfiguration(
        logger_name="windows_technician",
        log_directory=log_directory,
        log_filename="windows-technician.log",
        level=logging.INFO,
    )


def configure_logger(
    configuration: LoggingConfiguration,
) -> logging.Logger:
    if not isinstance(
        configuration,
        LoggingConfiguration,
    ):
        raise TypeError(
            "configuration must be LoggingConfiguration."
        )

    configuration.log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(
        configuration.logger_name
    )

    logger.setLevel(configuration.level)

    return logger
