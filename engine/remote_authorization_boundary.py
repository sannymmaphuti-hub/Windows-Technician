from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.remote_decision_boundary import RemoteDecisionBoundary
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class RemoteAuthorizationBoundary:
    """
    V1.0 remote authorization integration.

    Remote remediation authorization is delegated entirely to the
    canonical ProductionProblemSolvingEngine authorization boundary.

    This class does not:
    - implement authorization rules
    - automatically authorize actions
    - execute remediation
    - bind operations
    - verify remediation
    """

    def __init__(
        self,
        case,
        workflow=None,
        diagnostic_registry=None,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "RemoteAuthorizationBoundary requires a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteAuthorizationBoundary requires a case with REMOTE origin."
            )

        if workflow is None:
            workflow = TechnicianWorkflow(case)

        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "RemoteAuthorizationBoundary requires a TechnicianWorkflow."
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
                "RemoteAuthorizationBoundary requires a "
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

    def prepare(self):
        """
        Prepare canonical remediation actions and unauthorized
        authorization records.

        No action is authorized or executed by this method.
        """
        return self.engine.prepare_remediation_authorization()

    def authorize(
        self,
        action_id,
        *,
        technician=False,
    ):
        """
        Explicitly authorize an already-prepared remediation action.

        Authorization is delegated to the canonical production engine.
        """
        return self.engine.authorize_remediation(
            action_id,
            technician=technician,
        )

    def deny(
        self,
        action_id,
        *,
        technician=False,
    ):
        """
        Explicitly deny an already-prepared remediation action.
        """
        return self.engine.deny_remediation(
            action_id,
            technician=technician,
        )

    def authorization_for(self, action_id):
        """
        Return the canonical authorization record.
        """
        return self.engine.authorization_for(action_id)

    def authorization_allows_execution(self, action_id):
        """
        Read-only authorization check.

        This does not execute remediation.
        """
        return self.engine.authorization_allows_execution(
            action_id
        )

    @property
    def remediation_actions(self):
        """
        Return the canonical prepared remediation actions.
        """
        return deepcopy(self.engine.remediation_actions)

    @property
    def authorizations(self):
        """
        Return canonical authorization records.
        """
        return deepcopy(self.engine.authorizations)
