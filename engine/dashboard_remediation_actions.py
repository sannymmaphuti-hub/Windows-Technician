from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)


class DashboardRemediationActions:
    """
    Presentation adapter for remediation actions already produced
    by the intelligence/diagnostic pipeline.

    This component does not create, authorize, execute, retry,
    verify, or modify remediation actions.
    """

    def __init__(self, dashboard_view_model):
        if dashboard_view_model is None:
            raise ValueError("dashboard_view_model is required.")

        self.dashboard_view_model = dashboard_view_model
        self._models = []
        self.refresh()

    def refresh(self):
        intelligence = self.dashboard_view_model.intelligence

        actions = intelligence.get("remediation_actions")

        if not isinstance(actions, list):
            actions = []

        self._models = [
            RemediationPresentationModel(action)
            for action in actions
            if isinstance(action, dict)
        ]

    def models(self):
        return list(self._models)

    def count(self):
        return len(self._models)

    def to_dict(self):
        return [
            model.to_dict()
            for model in self._models
        ]
