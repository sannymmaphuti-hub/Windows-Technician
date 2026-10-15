"""Persistent logging and uncaught-exception handling for packaged builds."""

from __future__ import annotations

import logging
import logging.handlers
import sys
import threading
from pathlib import Path
from types import TracebackType
from typing import Callable


_LOGGER_PREFIX = "WindowsTechnician"
_HANDLER_MARKER = "_windows_technician_managed_handler"
_previous_sys_hook = None
_previous_thread_hook = None
_installed_sys_hook = None
_installed_thread_hook = None


def configure_packaged_crash_logging(
    app_name: str,
    user_data_root: str | Path,
    *,
    max_bytes: int = 2 * 1024 * 1024,
    backup_count: int = 5,
) -> tuple[logging.Logger, Path]:
    """Configure a rotating log under writable user application data."""
    if not isinstance(app_name, str) or not app_name.strip():
        raise ValueError("app_name must be a non-empty string.")

    if max_bytes < 1:
        raise ValueError("max_bytes must be positive.")

    if backup_count < 0:
        raise ValueError("backup_count cannot be negative.")

    data_root = Path(user_data_root).expanduser().resolve()
    log_directory = data_root / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_path = log_directory / "application.log"

    logger = logging.getLogger(f"{_LOGGER_PREFIX}.{app_name}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid duplicate file handlers when startup configuration is repeated.
    managed_handler = next(
        (
            handler
            for handler in logger.handlers
            if getattr(handler, _HANDLER_MARKER, False)
        ),
        None,
    )

    if managed_handler is None:
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
            delay=True,
        )
        setattr(handler, _HANDLER_MARKER, True)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s"
            )
        )
        logger.addHandler(handler)

    return logger, log_path


def install_uncaught_exception_handlers(
    logger: logging.Logger,
) -> None:
    """Install idempotent crash hooks while preserving current runtime hooks."""
    global _previous_sys_hook, _previous_thread_hook
    global _installed_sys_hook, _installed_thread_hook

    if not isinstance(logger, logging.Logger):
        raise TypeError("logger must be a logging.Logger instance.")

    # Reinstall if another component or test restored the runtime hook.
    if (
        _installed_sys_hook is None
        or sys.excepthook is not _installed_sys_hook
    ):
        _previous_sys_hook = sys.excepthook
        previous_hook = _previous_sys_hook

        def main_exception_hook(
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_traceback: TracebackType | None,
        ) -> None:
            try:
                logger.critical(
                    "Uncaught main-thread exception",
                    exc_info=(exc_type, exc_value, exc_traceback),
                )
            finally:
                previous_hook(exc_type, exc_value, exc_traceback)

        _installed_sys_hook = main_exception_hook
        sys.excepthook = main_exception_hook

    if hasattr(threading, "excepthook"):
        if (
            _installed_thread_hook is None
            or threading.excepthook is not _installed_thread_hook
        ):
            _previous_thread_hook = threading.excepthook
            previous_thread_hook = _previous_thread_hook

            def thread_exception_hook(args) -> None:
                try:
                    logger.critical(
                        "Uncaught background-thread exception in %s",
                        args.thread.name if args.thread else "<unknown>",
                        exc_info=(
                            args.exc_type,
                            args.exc_value,
                            args.exc_traceback,
                        ),
                    )
                finally:
                    previous_thread_hook(args)

            _installed_thread_hook = thread_exception_hook
            threading.excepthook = thread_exception_hook
