from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteRemediationExecution:
    """
    V1.0 remote remediation execution boundary.

    Remote remediation uses the canonical
    ProductionProblemSolvingEngine execution lifecycle.

    This class does not:
    - create remediation operations
    - bind operations
    - authorize remediation
    - verify remediation
    - create a second workflow
    - implement a second remediation lifecycle
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
                "RemoteRemediationExecution requires "
                "a RemoteRemediationContext."
            )

        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteRemediationExecution requires "
                "a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteRemediationExecution requires "
                "a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "RemoteRemediationExecution requires "
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
                "RemoteRemediationExecution requires "
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
                "RemoteRemediationExecution requires "
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

        self._last_result = None

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
    def result(self):
        if self._last_result is None:
            return None

        return deepcopy(self._last_result)

    def execute(
        self,
        action_id,
        expected=None,
        observed=None,
    ):
        """
        Execute an already-authorized, already-bound remediation
        action through the canonical production engine.
        """

        if not self.context.machine.is_available:
            raise ValueError(
                "Remote remediation requires an available machine."
            )

        result = self.engine.execute_remediation(
            action_id,
            expected=expected,
            observed=observed,
        )

        self._last_result = deepcopy(result)

        return result
