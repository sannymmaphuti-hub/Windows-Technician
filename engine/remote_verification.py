from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_remediation_context import RemoteRemediationContext
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteVerification:
    """
    V1.0 remote verification boundary.

    Remote remediation verification delegates entirely to the
    canonical ProductionProblemSolvingEngine verification lifecycle.

    This class does not:
    - implement verification rules
    - create a second verifier
    - execute remediation
    - retry remediation
    - create a second workflow
    - create a second recovery lifecycle
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
                "RemoteVerification requires "
                "a RemoteRemediationContext."
            )

        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteVerification requires "
                "a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteVerification requires "
                "a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "RemoteVerification requires "
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
                "RemoteVerification requires "
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
                "RemoteVerification requires "
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
    def verification_result(self):
        if self._last_result is None:
            return None

        return deepcopy(self._last_result)

    @property
    def verification_complete(self):
        return self.engine.verification_complete

    def verify(
        self,
        result=None,
        expected=None,
        observed=None,
    ):
        """
        Verify the remote remediation through the canonical
        ProductionProblemSolvingEngine boundary.
        """

        verification = self.engine.verify_remediation(
            result=result,
            expected=expected,
            observed=observed,
        )

        self._last_result = deepcopy(verification)

        return verification
