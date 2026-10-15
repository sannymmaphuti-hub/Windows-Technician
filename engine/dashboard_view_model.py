from copy import deepcopy

from engine.technician_dashboard import TechnicianDashboard


class DashboardViewModel:
    """
    Read-only presentation model for the Windows Technician
    dashboard.

    The dashboard presents intelligence and canonical technician
    dashboard projections but does not perform diagnosis, reasoning,
    recommendation, authorization, remediation, execution, or
    verification.
    """

    def __init__(self, application_state, intelligence=None):
        if application_state is None:
            raise ValueError("application_state is required.")

        self.application_state = application_state
        self.intelligence = (
            deepcopy(intelligence)
            if isinstance(intelligence, dict)
            else {}
        )
        self._dashboard_projection = {}

    def update_intelligence(self, intelligence):
        if intelligence is None:
            self.intelligence = {}
            return

        if not isinstance(intelligence, dict):
            raise ValueError("intelligence must be a dictionary.")

        self.intelligence = deepcopy(intelligence)

    def bind_dashboard(self, dashboard):
        """
        Bind the canonical TechnicianDashboard composition boundary.

        The view model receives a defensive presentation snapshot.
        It never receives permission to operate the dashboard or
        underlying platform objects.
        """
        if not isinstance(dashboard, TechnicianDashboard):
            raise ValueError(
                "dashboard must be a TechnicianDashboard."
            )

        self._dashboard_projection = deepcopy(
            dashboard.dashboard_projection()
        )

    def clear_dashboard(self):
        """Remove the current technician dashboard projection."""
        self._dashboard_projection = {}

    def health(self):
        health = self.intelligence.get("health")

        if not isinstance(health, dict):
            return {}

        return deepcopy(health)

    def findings(self):
        findings = self.intelligence.get("system_findings")

        if not isinstance(findings, list):
            return []

        return deepcopy(findings)

    def relationships(self):
        relationships = self.intelligence.get("relationships")

        if not isinstance(relationships, list):
            return []

        return deepcopy(relationships)

    def root_causes(self):
        root_causes = self.intelligence.get("root_causes")

        if not isinstance(root_causes, list):
            return []

        return deepcopy(root_causes)

    def recommendations(self):
        recommendations = self.intelligence.get("recommendations")

        if not isinstance(recommendations, list):
            return []

        return deepcopy(recommendations)

    def _operational_surface(self, key):
        """
        Read a production dashboard projection when one is bound;
        otherwise preserve the existing intelligence-backed contract.
        """
        if key in self._dashboard_projection:
            value = self._dashboard_projection.get(key)
        else:
            value = self.intelligence.get(key)

        if not isinstance(value, list):
            return []

        return deepcopy(value)

    def active_cases(self):
        return self._operational_surface("active_cases")

    def fleet_alerts(self):
        return self._operational_surface("fleet_alerts")

    def unresolved_problems(self):
        return self._operational_surface("unresolved_problems")

    def remediation_status(self):
        return self._operational_surface("remediation_status")

    def verification_status(self):
        return self._operational_surface("verification_status")

    def recent_activity(self):
        return self._operational_surface("recent_activity")

    def summary(self):
        health = self.health()

        return {
            "status": health.get("status", "UNKNOWN"),
            "health_score": health.get("score"),
            "finding_count": len(self.findings()),
            "relationship_count": len(self.relationships()),
            "root_cause_count": len(self.root_causes()),
            "recommendation_count": len(self.recommendations()),
            "machine_id": self.application_state.active_machine_id,
            "case_id": self.application_state.active_case_id,
        }

    def to_dict(self):
        return {
            "summary": self.summary(),
            "health": self.health(),
            "findings": self.findings(),
            "relationships": self.relationships(),
            "root_causes": self.root_causes(),
            "recommendations": self.recommendations(),
            "active_cases": self.active_cases(),
            "fleet_alerts": self.fleet_alerts(),
            "unresolved_problems": self.unresolved_problems(),
            "remediation_status": self.remediation_status(),
            "verification_status": self.verification_status(),
            "recent_activity": self.recent_activity(),
        }
