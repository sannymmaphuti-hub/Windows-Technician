from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteTechnicianProjection:
    """
    V1.0 remote technician projection boundary.

    Remote technician projection is a read-only projection of the
    canonical ProductionProblemSolvingEngine lifecycle with remote
    execution identity attached.

    This class does not:
    - create a second lifecycle
    - create a second workflow
    - diagnose
    - reason
    - authorize remediation
    - execute remediation
    - verify remediation
    - create recovery cycles
    - mutate the canonical engine
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
                "RemoteTechnicianProjection requires "
                "a RemoteRemediationContext."
            )

        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteTechnicianProjection requires "
                "a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteTechnicianProjection requires "
                "a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "RemoteTechnicianProjection requires "
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
                "RemoteTechnicianProjection requires "
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
                "RemoteTechnicianProjection requires "
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

    def projection(self):
        """
        Return the canonical production projection with remote
        execution identity attached.

        The canonical ProductionProblemSolvingEngine remains the
        single source of truth for lifecycle state.
        """
        projection = self.engine.projection()

        projection["machine_id"] = self.machine_id
        projection["hostname"] = self.hostname
        projection["session_id"] = self.session_id
        projection["is_remote"] = True

        return deepcopy(projection)
