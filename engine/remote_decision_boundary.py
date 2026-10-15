from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteDecisionBoundary:
    """
    V1.0 remote decision integration.

    Remote cases use the canonical ProductionProblemSolvingEngine
    decision boundary. This class does not implement a second remote
    decision engine and does not authorize or execute remediation.
    """

    def __init__(
        self,
        case,
        workflow=None,
        diagnostic_registry=None,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteDecisionBoundary requires a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteDecisionBoundary requires a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "RemoteDecisionBoundary requires a TechnicianWorkflow."
            )

        if workflow.case is not case:
            raise ValueError(
                "TechnicianWorkflow does not belong to the DiagnosticCase."
            )

        if diagnostic_registry is None:
            diagnostic_registry = WindowsDiagnosticEngineRegistry()

        if not isinstance(
            diagnostic_registry,
            WindowsDiagnosticEngineRegistry,
        ):
            raise ValueError(
                "RemoteDecisionBoundary requires a "
                "WindowsDiagnosticEngineRegistry."
            )

        self.case = case
        self.workflow = workflow
        self.diagnostic_registry = diagnostic_registry

        self.engine = ProductionProblemSolvingEngine(
            case=self.case,
            workflow=self.workflow,
            diagnostic_registry=self.diagnostic_registry,
        )

        self._decision = None

    @property
    def decision(self):
        if self._decision is None:
            return None
        return deepcopy(self._decision)

    @property
    def eligible(self):
        if self._decision is None:
            return None
        return self._decision.eligible

    @property
    def recommendation_type(self):
        if self._decision is None:
            return None
        return self._decision.recommendation_type

    def evaluate(self):
        """
        Evaluate the remote case through the canonical
        ProductionProblemSolvingEngine decision boundary.
        """

        decision = self.engine.evaluate_action_requirement()

        self._decision = deepcopy(decision)

        return deepcopy(decision)
