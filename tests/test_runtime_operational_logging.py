from engine.application_logging import ApplicationLogger
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)


def test_runtime_operational_logger_requires_application_logger():
    try:
        RuntimeOperationalLogger(None)
    except TypeError:
        pass
    else:
        raise AssertionError(
            "RuntimeOperationalLogger must require ApplicationLogger."
        )


def test_application_starting_event(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    entry = runtime_logger.application_starting()

    assert "[ApplicationRuntime]" in entry
    assert "[APPLICATION_STARTING]" in entry
    assert "startup has begun" in entry


def test_application_running_event(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    entry = runtime_logger.application_running()

    assert "[APPLICATION_RUNNING]" in entry
    assert "is running" in entry


def test_application_recovery_event_is_warning(tmp_path):
    path = tmp_path / "application.log"
    logger = ApplicationLogger(path)
    runtime_logger = RuntimeOperationalLogger(logger)

    runtime_logger.application_recovery()

    content = path.read_text(encoding="utf-8")

    assert "WARNING" in content
    assert "[APPLICATION_RECOVERY]" in content


def test_application_degraded_event_is_warning(tmp_path):
    path = tmp_path / "application.log"
    logger = ApplicationLogger(path)
    runtime_logger = RuntimeOperationalLogger(logger)

    runtime_logger.application_degraded()

    content = path.read_text(encoding="utf-8")

    assert "WARNING" in content
    assert "[APPLICATION_DEGRADED]" in content


def test_application_failed_event_is_error(tmp_path):
    path = tmp_path / "application.log"
    logger = ApplicationLogger(path)
    runtime_logger = RuntimeOperationalLogger(logger)

    runtime_logger.application_failed("startup failed")

    content = path.read_text(encoding="utf-8")

    assert "ERROR" in content
    assert "[APPLICATION_FAILED]" in content
    assert "startup failed" in content


def test_application_stopping_event(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    entry = runtime_logger.application_stopping()

    assert "[APPLICATION_STOPPING]" in entry
    assert "shutdown has begun" in entry


def test_application_stopped_event(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    entry = runtime_logger.application_stopped()

    assert "[APPLICATION_STOPPED]" in entry
    assert "stopped cleanly" in entry


def test_custom_event_is_written_to_application_logger(tmp_path):
    path = tmp_path / "application.log"
    logger = ApplicationLogger(path)
    runtime_logger = RuntimeOperationalLogger(logger)

    runtime_logger.log_event(
        "SERVICE_STARTING",
        "Diagnostics service is starting.",
    )

    content = path.read_text(encoding="utf-8")

    assert "[SERVICE_STARTING]" in content
    assert "Diagnostics service is starting." in content


def test_custom_event_rejects_empty_event(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    try:
        runtime_logger.log_event("", "message")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Empty event must be rejected."
        )


def test_custom_event_rejects_empty_message(tmp_path):
    logger = ApplicationLogger(tmp_path / "application.log")
    runtime_logger = RuntimeOperationalLogger(logger)

    try:
        runtime_logger.log_event("EVENT", "")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Empty message must be rejected."
        )
