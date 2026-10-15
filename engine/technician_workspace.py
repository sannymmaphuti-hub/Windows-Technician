from copy import deepcopy

from engine.technician_workflow import TechnicianWorkflow
from engine.technician_dashboard_presenter import TechnicianDashboardPresenter
from engine.technician_case_summary import TechnicianCaseSummary
from packaging.remediation_authorization import RemediationAuthorization
from engine.system_wide_intelligence_projection import SystemWideIntelligenceProjection


class TechnicianWorkspace:
    """Canonical V1.0 workspace composition and read-only presentation boundary."""

    def __init__(
        self,
        workflow,
        dashboard=None,
        case_summary=None,
        authorization=None,
        intelligence=None,
        *,
        intelligence_projection=None,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError("TechnicianWorkspace requires a TechnicianWorkflow.")
        if dashboard is not None and not isinstance(dashboard, TechnicianDashboardPresenter):
            raise ValueError("dashboard must be a TechnicianDashboardPresenter.")

        if case_summary is None:
            case_summary = TechnicianCaseSummary(workflow)
        elif not isinstance(case_summary, TechnicianCaseSummary):
            raise ValueError("case_summary must be a TechnicianCaseSummary.")
        if case_summary.workflow is not workflow:
            raise ValueError("case_summary belongs to a different workflow.")

        if authorization is not None and not isinstance(authorization, RemediationAuthorization):
            raise ValueError("authorization must be a RemediationAuthorization.")
        if (
            intelligence is not None
            and intelligence_projection is not None
            and intelligence is not intelligence_projection
        ):
            raise ValueError(
                "Provide either intelligence or intelligence_projection, "
                "not conflicting projections."
            )
        selected_intelligence = (
            intelligence_projection if intelligence_projection is not None else intelligence
        )
        if selected_intelligence is not None and not isinstance(
            selected_intelligence, SystemWideIntelligenceProjection
        ):
            raise ValueError(
                "intelligence_projection must be a SystemWideIntelligenceProjection."
            )

        self.workflow = workflow
        self.dashboard = dashboard
        self.case_summary = case_summary
        self._authorization = authorization
        self.intelligence = selected_intelligence

    @property
    def case(self):
        return self.workflow.case

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def machine_id(self):
        return self.case.machine_id

    @property
    def hostname(self):
        return self.case.hostname

    @property
    def state(self):
        return self.workflow.state

    @property
    def is_terminal(self):
        return self.workflow.is_terminal

    @property
    def history(self):
        return self.workflow.history

    @property
    def findings(self):
        return deepcopy(self.case.findings)

    @property
    def root_causes(self):
        return deepcopy(self.case.root_causes)

    @property
    def recommendations(self):
        return deepcopy(self.case.recommendations)

    @property
    def decision(self):
        return self.case_summary.decision

    @property
    def remediation_status(self):
        return self.case_summary.remediation_status

    @property
    def verification_status(self):
        return self.case_summary.verification_status

    @property
    def escalation_status(self):
        return self.case_summary.escalation_status

    @property
    def authorization(self):
        return self._authorization

    @property
    def dashboard_presenter(self):
        return self.dashboard

    def bind_dashboard_presenter(self, presenter):
        if not isinstance(presenter, TechnicianDashboardPresenter):
            raise ValueError("presenter must be a TechnicianDashboardPresenter.")
        self.dashboard = presenter

    def clear_dashboard_presenter(self):
        self.dashboard = None

    def dashboard_snapshot(self):
        if self.dashboard is None:
            return {}
        return deepcopy(self.dashboard.snapshot())

    def dashboard_projection(self):
        return self.dashboard_snapshot()

    @property
    def intelligence_projection(self):
        return self.intelligence

    def bind_intelligence_projection(self, projection):
        if not isinstance(projection, SystemWideIntelligenceProjection):
            raise ValueError("projection must be a SystemWideIntelligenceProjection.")
        self.intelligence = projection

    def clear_intelligence_projection(self):
        self.intelligence = None

    def intelligence_snapshot(self):
        if self.intelligence is None:
            return {}

        return deepcopy({
            "case": {
                "case_id": self.case.case_id,
                "state": self.workflow.state,
            },
            "intelligence": self.intelligence.intelligence(),
        })

    def intelligence_data_projection(self):
        return self.intelligence_snapshot()

    def historical_intelligence(self):
        if self.intelligence is None:
            return {}
        return deepcopy(self.intelligence.historical())

    @staticmethod
    def _enum_value(value):
        if value is None:
            return None
        return getattr(value, "value", value)

    def _effective_authorization(self):
        if self._authorization is not None:
            return self._authorization
        if isinstance(self.case_summary.decision, RemediationAuthorization):
            return self.case_summary.decision
        return None

    def _authorization_projection(self):
        authorization = self._effective_authorization()
        if authorization is None:
            return {"state": "UNAUTHORIZED", "reason": "NOT_REQUESTED", "action_id": None}
        return {
            "state": self._enum_value(authorization.state),
            "reason": self._enum_value(authorization.reason),
            "action_id": authorization.action_id,
        }

    def technician_actions(self):
        """Return defensive, read-only technician action projections."""
        actions = []
        authorization = self._authorization_projection()
        decision = self.case_summary.decision

        for recommendation in self.case.recommendations:
            recommendation_copy = deepcopy(recommendation)
            if isinstance(recommendation_copy, dict):
                action_name = (
                    recommendation_copy.get("action")
                    or recommendation_copy.get("recommendation")
                    or recommendation_copy.get("id")
                )
            else:
                action_name = recommendation_copy

            actions.append({
                "case_id": self.case.case_id,
                "action": action_name,
                "decision": deepcopy(decision),
                "authorization": deepcopy(authorization),
                "recommendations": [recommendation_copy],
            })

        return deepcopy(actions)

    def _project_value(self, value):
        if value is None:
            return None
        projection_method = getattr(value, "projection", None)
        if callable(projection_method):
            return deepcopy(projection_method())
        return deepcopy(value)

    def case_projection(self):
        summary = self.case_summary
        projection = {
            "case": {
                "case_id": self.case.case_id,
                "state": self.workflow.state,
                "is_terminal": self.workflow.is_terminal,
            },
            "findings": self.case.findings,
            "root_causes": self.case.root_causes,
            "recommendations": self.case.recommendations,
            "decision": summary.decision,
            "notes": summary.notes,
            "remediation_status": summary.remediation_status,
            "verification_status": summary.verification_status,
            "escalation_status": summary.escalation_status,
            "history": self.workflow.history,
            "closure": self._project_value(getattr(summary, "closure", None)),
            "reasoning_summary": self._project_value(
                getattr(summary, "reasoning_summary", None)
            ),
        }

        # Preserve the established exact key set for cases with no recommendations.
        if self.case.recommendations:
            projection["technician_actions"] = self.technician_actions()

        return deepcopy(projection)

    def projection(self):
        intelligence = self.intelligence_snapshot()

        if self.intelligence is not None:
            intelligence["historical"] = self.historical_intelligence()

        return deepcopy({
            "case": self.case_projection(),
            "dashboard": self.dashboard_snapshot(),
            "intelligence": intelligence,
        })

    def __repr__(self):
        return f"TechnicianWorkspace(case_id={self.case_id!r}, state={self.state!r})"
