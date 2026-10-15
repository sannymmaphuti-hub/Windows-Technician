from pathlib import Path
from packaging.packaged_crash_logging import (
    configure_packaged_crash_logging,
    install_uncaught_exception_handlers,
)
from packaging.runtime_path_boundaries import resolve_application_paths
import sys

from PySide6.QtWidgets import QApplication

from engine.application_bootstrap import ApplicationBootstrap
from engine.application_logging import ApplicationLogger
from engine.application_state import ApplicationState
from engine.main_window import create_main_window

from packaging.application_metadata import APPLICATION_METADATA
from packaging.configuration_environment_architecture import (
    build_configuration_environment_architecture,
)
from packaging.production_configuration import (
    build_production_configuration_from_environment,
)
from packaging.runtime_configuration import (
    initialize_runtime_paths,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)


APP_NAME = APPLICATION_METADATA.display_name
APP_VERSION = APPLICATION_METADATA.version


def _project_root() -> Path:
    """Return the Windows Technician application project root."""
    return resolve_application_paths(
        app_name=APP_NAME,
        module_file=__file__,
    ).resource_root


def _application_state_from_runtime(
    runtime,
    *,
    configuration=None,
) -> ApplicationState:
    """
    Translate the production runtime into the canonical UI state.

    ApplicationRuntime owns lifecycle and services.
    ApplicationState owns application-level state consumed by
    the presentation layer.
    """
    configuration_data = {}

    if configuration is not None:
        configuration_data = dict(
            configuration.state.configuration
        )

    lifecycle_state = runtime.lifecycle.state

    status_map = {
        "CREATED": "STARTING",
        "STARTING": "STARTING",
        "RUNNING": "READY",
        "DEGRADED": "ERROR",
        "FAILED": "ERROR",
        "STOPPING": "STOPPING",
        "STOPPED": "STOPPED",
    }

    status = status_map.get(
        lifecycle_state.name,
        "ERROR",
    )

    return ApplicationState(
        application_name=APP_NAME,
        version=APP_VERSION,
        status=status,
        configuration=configuration_data,
    )


def create_application():
    """
    Create the Qt application and production bootstrap.

    Production startup assembly:

        QApplication
            ↓
        Runtime Paths
            ↓
        Configuration Environment
            ↓
        Production Configuration
            ↓
        Operational State
            ↓
        Operational Logging
            ↓
        ApplicationBootstrap
    """
    qt_application = QApplication.instance()

    if qt_application is None:
        qt_application = QApplication(sys.argv)

    runtime_paths = initialize_runtime_paths()
    crash_logger, crash_log_path = configure_packaged_crash_logging(
        APP_NAME,
        runtime_paths.application_data,
    )
    install_uncaught_exception_handlers(crash_logger)

    project_root = _project_root()
    application_paths = resolve_application_paths(
        app_name=APP_NAME,
        module_file=__file__,
    )

    configuration_architecture = (
        build_configuration_environment_architecture(
            project_root=project_root,
            user_data_root=runtime_paths.application_data,
            system_data_root=application_paths.application_root,
        )
    )

    production_configuration = (
        build_production_configuration_from_environment(
            configuration_architecture,
        )
    )

    operational_state = (
        RuntimeOperationalState.from_runtime_paths(
            runtime_paths
        )
    )

    application_logger = ApplicationLogger(
        runtime_paths.logs / "application.log"
    )

    operational_logger = RuntimeOperationalLogger(
        application_logger
    )

    bootstrap = ApplicationBootstrap(
        application_name=APP_NAME,
        version=APP_VERSION,
        configuration=production_configuration,
        operational_state=operational_state,
        operational_logger=operational_logger,
    )

    return qt_application, bootstrap


def start_application():
    """
    Start Windows Technician.

    Production startup sequence:

        QApplication
            ↓
        Runtime Paths
            ↓
        Configuration Environment
            ↓
        Production Configuration
            ↓
        Operational State Recovery
            ↓
        Operational Logging
            ↓
        ApplicationBootstrap
            ↓
        ApplicationRuntime
            ↓
        ApplicationState
            ↓
        MainWindow
            ↓
        Dashboard
    """
    qt_application, bootstrap = create_application()

    runtime = bootstrap.start()

    if not bootstrap.started:
        return qt_application, bootstrap, None

    try:
        application_state = bootstrap.state

        window = create_main_window(application_state)
        window.show()

        return qt_application, bootstrap, window
    except Exception:
        bootstrap.stop()
        raise


def main():
    """
    Application entry point.
    """
    qt_application, bootstrap, window = start_application()

    if window is None:
        return 1

    try:
        return qt_application.exec()
    finally:
        bootstrap.stop()


if __name__ == "__main__":
    raise SystemExit(main())
