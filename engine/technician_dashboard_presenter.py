from copy import deepcopy


class TechnicianDashboardPresenter:
    """
    UI-facing adapter for the canonical DashboardViewModel.

    This class only reads presentation data. It never diagnoses,
    reasons, authorizes, executes, or verifies.
    """

    def __init__(self, view_model):
        if view_model is None:
            raise ValueError("view_model is required.")

        self.view_model = view_model

    def machine_health(self):
        return deepcopy(
            self.view_model.to_dict().get("health", {})
        )

    def active_cases(self):
        return deepcopy(
            self.view_model.active_cases()
        )

    def fleet_alerts(self):
        return deepcopy(
            self.view_model.fleet_alerts()
        )

    def unresolved_problems(self):
        return deepcopy(
            self.view_model.unresolved_problems()
        )

    def remediation_status(self):
        return deepcopy(
            self.view_model.remediation_status()
        )

    def verification_status(self):
        return deepcopy(
            self.view_model.verification_status()
        )

    def recent_activity(self):
        return deepcopy(
            self.view_model.recent_activity()
        )

    def snapshot(self):
        return {
            "health": self.machine_health(),
            "active_cases": self.active_cases(),
            "fleet_alerts": self.fleet_alerts(),
            "unresolved_problems": self.unresolved_problems(),
            "remediation_status": self.remediation_status(),
            "verification_status": self.verification_status(),
            "recent_activity": self.recent_activity(),
        }
