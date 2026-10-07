from engine.application_bootstrap import ApplicationBootstrap
from engine.application_logging import ApplicationLogger
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)


def build_operational_state(tmp_path):
    from packaging.runtime_configuration import RuntimePaths

    paths = RuntimePaths(
        application_data=tmp_path,
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    return RuntimeOperationalState.from_runtime_paths(paths)


def build_logger(tmp_path):
    return RuntimeOperationalLogger(
        ApplicationLogger(tmp_path / "application.log")
    )


def test_fresh_start_does_not_log_recovery(tmp_path):
    operational_state = build_operational_state(tmp_path)
    logger = build_logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational_state,
        operational_logger=logger,
    )

    bootstrap.start()

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_RUNNING]" in content
    assert "[APPLICATION_RECOVERY]" not in content


def test_unclean_previous_session_logs_recovery(tmp_path):
    operational_state = build_operational_state(tmp_path)

    operational_state.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
        recovered=False,
    )

    logger = build_logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational_state,
        operational_logger=logger,
    )

    bootstrap.start()

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_RECOVERY]" in content
    assert "[APPLICATION_RUNNING]" in content


def test_clean_previous_session_does_not_log_recovery(tmp_path):
    operational_state = build_operational_state(tmp_path)

    operational_state.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
        recovered=False,
    )

    logger = build_logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational_state,
        operational_logger=logger,
    )

    bootstrap.start()

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_RECOVERY]" not in content


def test_recovery_event_is_logged_before_runtime_start_event(tmp_path):
    operational_state = build_operational_state(tmp_path)

    operational_state.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
        recovered=False,
    )

    logger = build_logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational_state,
        operational_logger=logger,
    )

    bootstrap.start()

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    recovery_position = content.index(
        "[APPLICATION_RECOVERY]"
    )
    starting_position = content.index(
        "[APPLICATION_STARTING]"
    )

    assert recovery_position < starting_position
