import logging
import sys
import threading

import pytest

from packaging.packaged_crash_logging import (
    configure_packaged_crash_logging,
    install_uncaught_exception_handlers,
)


def test_logs_are_created_under_user_data(tmp_path):
    logger, log_path = configure_packaged_crash_logging(
        "TestApplication",
        tmp_path / "UserData",
    )

    logger.info("packaged runtime test")

    for handler in logger.handlers:
        handler.flush()

    assert log_path.parent == (tmp_path / "UserData" / "logs").resolve()
    assert log_path.exists()
    assert "packaged runtime test" in log_path.read_text(encoding="utf-8")


def test_log_handler_is_rotating(tmp_path):
    logger, _ = configure_packaged_crash_logging(
        "RotationTest",
        tmp_path,
        max_bytes=100,
        backup_count=2,
    )

    handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.handlers.RotatingFileHandler)
    ]

    assert handlers
    assert handlers[0].maxBytes == 100
    assert handlers[0].backupCount == 2


def test_repeated_configuration_does_not_duplicate_managed_handlers(tmp_path):
    logger, _ = configure_packaged_crash_logging(
        "IdempotenceTest",
        tmp_path,
    )
    first_count = sum(
        getattr(handler, "_windows_technician_managed_handler", False)
        for handler in logger.handlers
    )

    configure_packaged_crash_logging("IdempotenceTest", tmp_path)

    second_count = sum(
        getattr(handler, "_windows_technician_managed_handler", False)
        for handler in logger.handlers
    )

    assert first_count == second_count == 1


@pytest.mark.parametrize("app_name", ["", " ", None])
def test_invalid_app_name_is_rejected(tmp_path, app_name):
    with pytest.raises(ValueError, match="app_name"):
        configure_packaged_crash_logging(app_name, tmp_path)


def test_invalid_rotation_settings_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="max_bytes"):
        configure_packaged_crash_logging(
            "InvalidRotation",
            tmp_path,
            max_bytes=0,
        )

    with pytest.raises(ValueError, match="backup_count"):
        configure_packaged_crash_logging(
            "InvalidRotation",
            tmp_path,
            backup_count=-1,
        )


def test_exception_handler_installation_preserves_original_hook(tmp_path):
    import packaging.packaged_crash_logging as crash_logging

    logger, _ = configure_packaged_crash_logging(
        "ExceptionHookTest",
        tmp_path,
    )

    # Save both process hooks and all installer bookkeeping.
    actual_sys_hook = sys.excepthook
    actual_thread_hook = getattr(threading, "excepthook", None)

    original_state = (
        crash_logging._previous_sys_hook,
        crash_logging._previous_thread_hook,
        crash_logging._installed_sys_hook,
        crash_logging._installed_thread_hook,
    )

    try:
        # If a previous installation is still active, recover the hook
        # that installation wrapped. This establishes a clean baseline.
        baseline_sys_hook = (
            crash_logging._previous_sys_hook
            if actual_sys_hook is crash_logging._installed_sys_hook
            and crash_logging._previous_sys_hook is not None
            else actual_sys_hook
        )

        baseline_thread_hook = actual_thread_hook
        if actual_thread_hook is not None:
            if (
                actual_thread_hook is crash_logging._installed_thread_hook
                and crash_logging._previous_thread_hook is not None
            ):
                baseline_thread_hook = crash_logging._previous_thread_hook

        sys.excepthook = baseline_sys_hook
        if baseline_thread_hook is not None:
            threading.excepthook = baseline_thread_hook

        crash_logging._previous_sys_hook = None
        crash_logging._previous_thread_hook = None
        crash_logging._installed_sys_hook = None
        crash_logging._installed_thread_hook = None

        install_uncaught_exception_handlers(logger)

        assert sys.excepthook is not baseline_sys_hook

        if baseline_thread_hook is not None:
            assert threading.excepthook is not baseline_thread_hook

        # Verify that the original handlers were preserved for delegation.
        assert crash_logging._previous_sys_hook is baseline_sys_hook

        if baseline_thread_hook is not None:
            assert (
                crash_logging._previous_thread_hook
                is baseline_thread_hook
            )
    finally:
        # Restore the exact process state that existed before this test.
        sys.excepthook = actual_sys_hook

        if actual_thread_hook is not None:
            threading.excepthook = actual_thread_hook

        (
            crash_logging._previous_sys_hook,
            crash_logging._previous_thread_hook,
            crash_logging._installed_sys_hook,
            crash_logging._installed_thread_hook,
        ) = original_state
