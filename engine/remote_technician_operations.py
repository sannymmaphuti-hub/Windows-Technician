# ==========================================
# Windows Technician V1.0
# REMOTE TECHNICIAN OPERATIONS
# ==========================================

from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import (
    RemoteDiagnosticContext,
)
from engine.remote_diagnostic_input import (
    RemoteDiagnosticInput,
)
from engine.remote_diagnostic_pipeline import (
    RemoteDiagnosticPipeline,
)
from engine.windows_diagnostic_result_normalizer import (
    WindowsDiagnosticResultNormalizer,
)


class RemoteTechnicianOperations:
    """
    V1.0 remote technician orchestration boundary.

    Remote execution is an execution context for the
    canonical Windows Technician lifecycle.

    This class does NOT:
    - create a remote-specific DiagnosticCase
    - create a separate TechnicianWorkflow
    - authorize remediation
    - execute remediation
    - verify remediation
    - create recovery operations
    - implement diagnostic reasoning

    Existing remote diagnostic capabilities are composed
    and normalized into the canonical V1.0 result/case model.
    """

    def __init__(
        self,
        machine,
        session,
        diagnostic_pipeline=None,
    ):
        if not isinstance(
            machine,
            ManagedMachine,
        ):
            raise ValueError(
                "RemoteTechnicianOperations requires "
                "a ManagedMachine."
            )

        if not isinstance(
            session,
            RemoteSession,
        ):
            raise ValueError(
                "RemoteTechnicianOperations requires "
                "a RemoteSession."
            )

        if session.machine is not machine:
            raise ValueError(
                "RemoteSession does not belong to "
                "the supplied ManagedMachine."
            )

        if not machine.is_available:
            raise ValueError(
                "Remote operations require an available machine."
            )

        if diagnostic_pipeline is None:
            diagnostic_pipeline = RemoteDiagnosticPipeline()

        if not hasattr(
            diagnostic_pipeline,
            "diagnose",
        ):
            raise ValueError(
                "diagnostic_pipeline must provide "
                "a diagnose() method."
            )

        self.machine = machine
        self.session = session
        self.diagnostic_pipeline = diagnostic_pipeline

        self._last_result = None
        self._case = None

    @property
    def machine_id(self):
        return self.machine.machine_id

    @property
    def hostname(self):
        return self.machine.hostname

    @property
    def session_id(self):
        return self.session.session_id

    @property
    def is_remote(self):
        return True

    @property
    def result(self):
        return deepcopy(self._last_result)

    @property
    def case(self):
        return self._case

    def diagnose(self, observations):
        """
        Execute the existing remote diagnostic pipeline
        and convert its result into the canonical
        WindowsDiagnosticResult and DiagnosticCase.

        This method performs diagnosis only.

        It does not authorize or execute remediation.
        """

        if not self.machine.is_available:
            raise ValueError(
                "Remote diagnostics require "
                "an available machine."
            )

        context = RemoteDiagnosticContext(
            self.machine,
            self.session,
        )

        remote_input = RemoteDiagnosticInput(
            context,
            list(observations),
        )

        raw_result = self.diagnostic_pipeline.diagnose(
            remote_input
        )

        canonical = (
            WindowsDiagnosticResultNormalizer.normalize(
                raw_result
            )
        )

        self._last_result = canonical

        case = DiagnosticCase()

        case.set_observations(
            canonical.observations
        )

        case.set_signals(
            canonical.signals
        )

        case.set_findings(
            canonical.findings
        )

        case.set_correlations(
            canonical.correlations
        )

        case.set_root_causes(
            canonical.candidates
        )

        case.set_recommendations(
            canonical.recommendations
        )

        # Remote identity belongs to the canonical case.
        case.machine_id = self.machine_id
        case.hostname = self.hostname
        case.session_id = self.session_id
        case.origin = "REMOTE"

        if canonical.primary_cause is not None:
            case.set_primary_root_cause(
                canonical.primary_cause
            )

        self._case = case

        return case
