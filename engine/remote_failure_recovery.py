from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteFailureRecovery:
    """
    V1.0 remote failure and recovery boundary.

    Remote recovery delegates entirely to the canonical
    ProductionProblemSolvingEngine recovery lifecycle.

    This class does not:
    - create a second recovery workflow
    - retry remediation automatically
    - reauthorize remediation
    - execute remediation
    - execute diagnostics
    - create a second recovery history
    """

    def __init__(
        self,
        context,
        case,
        workflow=None,
        diagnostic_registry=None,
        engine=None,
    ):
        if not isinstance(
            context,
            RemoteRemediationContext,
        ):
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a RemoteRemediationContext."
            )

        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a TechnicianWorkflow."
            )

        if workflow.case is not case:
            raise ValueError(
                "TechnicianWorkflow does not belong "
                "to the DiagnosticCase."
            )

        if diagnostic_registry is None:
            diagnostic_registry = WindowsDiagnosticEngineRegistry()

        if not isinstance(
            diagnostic_registry,
            WindowsDiagnosticEngineRegistry,
        ):
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a WindowsDiagnosticEngineRegistry."
            )

        if engine is None:
            engine = ProductionProblemSolvingEngine(
                case=case,
                workflow=workflow,
                diagnostic_registry=diagnostic_registry,
            )

        if not isinstance(
            engine,
            ProductionProblemSolvingEngine,
        ):
            raise ValueError(
                "RemoteFailureRecovery requires "
                "a ProductionProblemSolvingEngine."
            )

        if engine.case is not case:
            raise ValueError(
                "ProductionProblemSolvingEngine does not "
                "belong to the DiagnosticCase."
            )

        if engine.workflow is not workflow:
            raise ValueError(
                "ProductionProblemSolvingEngine does not "
                "belong to the TechnicianWorkflow."
            )

        self.context = context
        self.case = case
        self.workflow = workflow
        self.diagnostic_registry = diagnostic_registry
        self.engine = engine

        self._last_cycle = None

    @property
    def machine_id(self):
        return self.context.machine_id

    @property
    def hostname(self):
        return self.context.hostname

    @property
    def session_id(self):
        return self.context.session_id

    @property
    def is_remote(self):
        return True

    @property
    def recovery_cycles(self):
        return deepcopy(self.engine.recovery_cycles)

    @property
    def recovery_cycle_count(self):
        return self.engine.recovery_cycle_count

    @property
    def current_recovery_cycle(self):
        return deepcopy(self.engine.current_recovery_cycle)

    @property
    def last_cycle(self):
        return deepcopy(self._last_cycle)

    def start_recovery_cycle(self):
        """
        Begin an explicit canonical recovery cycle.

        No retry, authorization, remediation, or diagnosis
        is performed by this boundary.
        """

        cycle = self.engine.start_recovery_cycle()

        self._last_cycle = deepcopy(cycle)

        return cycle

    def projection(self):
        """
        Return the canonical production projection while
        preserving remote execution identity.
        """

        projection = self.engine.projection()

        projection["machine_id"] = self.machine_id
        projection["hostname"] = self.hostname
        projection["session_id"] = self.session_id
        projection["is_remote"] = True

        return deepcopy(projection)
