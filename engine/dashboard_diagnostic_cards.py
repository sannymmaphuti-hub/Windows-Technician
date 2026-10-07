from engine.diagnostic_card_model import DiagnosticCardModel


class DashboardDiagnosticCards:
    """
    Presentation adapter that converts dashboard findings into
    DiagnosticCardModel instances.

    This component does not diagnose, reason, recommend,
    authorize, remediate, or execute.
    """

    def __init__(self, dashboard_view_model):
        if dashboard_view_model is None:
            raise ValueError("dashboard_view_model is required.")

        self.dashboard_view_model = dashboard_view_model
        self._cards = []

        self.refresh()

    def refresh(self):
        self._cards = [
            DiagnosticCardModel(finding)
            for finding in self.dashboard_view_model.findings()
            if isinstance(finding, dict)
        ]

    def cards(self):
        return list(self._cards)

    def count(self):
        return len(self._cards)
