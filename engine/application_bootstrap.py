"""Application bootstrap compatibility and production startup boundary."""

from engine.application_state import ApplicationState
from packaging.application_metadata import APPLICATION_METADATA

from packaging.application_runtime import (
    ApplicationRuntime,
    application_runtime_is_running,
    application_runtime_is_stopped,
    create_application_runtime,
    start_application_runtime,
    stop_application_runtime,
)
from packaging.production_configuration import (
    ProductionConfiguration,
    ProductionConfigurationResult,
    apply_production_configuration,
    production_configuration_allows_startup,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.startup_recovery import (
    StartupRecoveryContext,
    build_startup_recovery_context,
)
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
    get_application_service,
)


class ApplicationBootstrap:
    """
    Production startup boundary over the canonical application runtime.

    Bootstrap coordinates:

        configuration
            ↓
        recovery
            ↓
        runtime
            ↓
        services

    Runtime remains responsible for lifecycle execution.
    Bootstrap does not perform diagnostics, remediation, authorization,
    or execution.
    """

    def __init__(
        self,
        *,
        application_name="Windows Technician",
        version=APPLICATION_METADATA.version,
        configuration=None,
        operational_state=None,
        operational_logger=None,
    ):
        if not isinstance(application_name, str):
            raise TypeError(
                "application_name must be a string."
            )

        if not application_name.strip():
            raise ValueError(
                "application_name must be a non-empty string."
            )

        if not isinstance(version, str):
            raise TypeError(
                "version must be a string."
            )

        if not version.strip():
            raise ValueError(
                "version must be a non-empty string."
            )

        if (
            configuration is not None
            and not isinstance(
                configuration,
                ProductionConfiguration,
            )
        ):
            raise TypeError(
                "configuration must be a ProductionConfiguration "
                "or None."
            )

        if (
            operational_state is not None
            and not isinstance(
                operational_state,
                RuntimeOperationalState,
            )
        ):
            raise TypeError(
                "operational_state must be a RuntimeOperationalState "
                "or None."
            )

        if (
            operational_logger is not None
            and not isinstance(
                operational_logger,
                RuntimeOperationalLogger,
            )
        ):
            raise TypeError(
                "operational_logger must be a RuntimeOperationalLogger "
                "or None."
            )

        self.application_name = application_name
        self.version = version
        self.configuration = configuration
        self._operational_state = operational_state
        self._operational_logger = operational_logger
        self._startup_recovery = None
        self._configuration_result = None
        self._started = False

        self._runtime = create_application_runtime(
            operational_state=operational_state,
            operational_logger=operational_logger,
        )

        self._state = ApplicationState(
            application_name=self.application_name,
            version=self.version,
            status="STARTING",
            configuration=self._configuration_data(),
        )

    @property
    def runtime(self) -> ApplicationRuntime:
        return self._runtime

    @property
    def started(self) -> bool:
        return self._started

    @property
    def state(self) -> ApplicationState:
        """
        Compatibility/application state surface.

        The runtime remains authoritative for lifecycle state. This
        object is the application-level state consumed by the UI.
        """
        return self._state

    @property
    def operational_state(self):
        return self._operational_state

    @property
    def operational_logger(self):
        return self._operational_logger

    @property
    def startup_recovery(self) -> StartupRecoveryContext | None:
        return self._startup_recovery

    @property
    def recovery_required(self) -> bool:
        if self._startup_recovery is None:
            return False

        return self._startup_recovery.recovery_required

    @property
    def configuration_result(
        self,
    ) -> ProductionConfigurationResult | None:
        return self._configuration_result

    @property
    def startup_allowed(self) -> bool:
        if self._configuration_result is None:
            return True

        return production_configuration_allows_startup(
            self._configuration_result
        )

    def _configuration_data(self) -> dict:
        if self.configuration is None:
            return {}

        return dict(
            self.configuration.state.configuration
        )

    def _sync_state(self, status: str) -> None:
        self._state = ApplicationState(
            application_name=self.application_name,
            version=self.version,
            status=status,
            configuration=self._configuration_data(),
        )

    def _evaluate_configuration(self) -> bool:
        """
        Evaluate production configuration before runtime startup.

        Configuration application is intentionally non-mutating. The
        canonical configuration boundary determines whether startup
        is allowed.
        """
        if self.configuration is None:
            self._configuration_result = None
            return True

        self._configuration_result = (
            apply_production_configuration(
                self._runtime,
                self.configuration,
            )
        )

        return production_configuration_allows_startup(
            self._configuration_result
        )

    def _log_startup_blocked(self) -> None:
        if self._operational_logger is None:
            return

        self._operational_logger.application_failed(
            "Application startup blocked by production configuration."
        )

    def start(self) -> ApplicationRuntime:
        # A running bootstrap is already started. Return the same
        # runtime instead of attempting a second lifecycle transition.
        if self._started and application_runtime_is_running(
            self._runtime
        ):
            return self._runtime

        startup_allowed = self._evaluate_configuration()

        if not startup_allowed:
            self._log_startup_blocked()
            self._started = False
            self._sync_state("ERROR")
            return self._runtime

        if self._operational_state is not None:
            self._startup_recovery = (
                build_startup_recovery_context(
                    self._operational_state
                )
            )

            if (
                self._startup_recovery.recovery_required
                and self._operational_logger is not None
            ):
                self._operational_logger.application_recovery()

        if application_runtime_is_stopped(self._runtime):
            self._runtime = create_application_runtime(
                operational_state=self._operational_state,
                operational_logger=self._operational_logger,
            )

            if self.configuration is not None:
                self._configuration_result = (
                    apply_production_configuration(
                        self._runtime,
                        self.configuration,
                    )
                )

        self._runtime = start_application_runtime(
            self._runtime
        )

        self._started = application_runtime_is_running(
            self._runtime
        )

        self._sync_state(self._runtime.status)

        return self._runtime

    def stop(self) -> ApplicationRuntime | ApplicationState:
        if not self._started:
            # A stop request before startup is a compatibility-level
            # application-state transition only. The canonical runtime
            # remains CREATED so that startup remains possible.
            self._sync_state("STOPPED")
            return self._state

        self._runtime = stop_application_runtime(
            self._runtime
        )

        self._started = False
        self._sync_state(self._runtime.status)

        return self._runtime

    def fail(self) -> ApplicationState:
        """
        Mark bootstrap as failed without mutating runtime lifecycle.

        Runtime lifecycle failure remains the responsibility of the
        runtime/recovery architecture.
        """
        self._started = False
        self._sync_state("ERROR")
        return self._state

    def service_state(
        self,
        name: ApplicationServiceName,
    ) -> ApplicationServiceState:
        if not isinstance(name, ApplicationServiceName):
            raise TypeError(
                "name must be an ApplicationServiceName."
            )

        return get_application_service(
            self._runtime.services,
            name,
        ).state
