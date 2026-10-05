# ==========================================
# Windows Technician v0.8
# PROACTIVE RECOMMENDATION
# ==========================================

from engine.proactive_alert import ProactiveAlert


class ProactiveRecommendation:

    VALID_STATUSES = {
        "PENDING",
        "ACKNOWLEDGED",
        "DISMISSED",
    }

    def __init__(
        self,
        alert,
        recommendation,
    ):
        if not isinstance(alert, ProactiveAlert):
            raise ValueError(
                "ProactiveRecommendation requires a ProactiveAlert."
            )

        if recommendation is None:
            raise ValueError(
                "recommendation is required."
            )

        self.alert = alert
        self.recommendation = recommendation
        self.status = "PENDING"

    @property
    def machine_id(self):
        return self.alert.machine_id

    @property
    def hostname(self):
        return self.alert.hostname

    def acknowledge(self):
        if self.status == "PENDING":
            self.status = "ACKNOWLEDGED"

    def dismiss(self):
        if self.status in {"PENDING", "ACKNOWLEDGED"}:
            self.status = "DISMISSED"