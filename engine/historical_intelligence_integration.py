from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_deviation_detection import HistoricalDeviationDetection
from engine.historical_health_baseline import HistoricalHealthBaseline
from engine.historical_problem_recurrence import HistoricalProblemRecurrence
from engine.historical_trend_intelligence import HistoricalTrendIntelligence


class HistoricalIntelligenceIntegration:
    """
    Canonical V1.0 historical intelligence composition boundary.

    Composes the existing historical intelligence components into
    one read-only projection surface.

    This class does not:
    - create a second history model
    - mutate DiagnosticCase
    - mutate DiagnosticHistory
    - diagnose
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(
        self,
        history,
        trends=None,
        recurrence=None,
        baseline=None,
        deviation=None,
    ):
        if not isinstance(history, DiagnosticHistory):
            raise ValueError(
                "HistoricalIntelligenceIntegration requires "
                "a DiagnosticHistory."
            )

        if trends is None:
            trends = HistoricalTrendIntelligence(history)

        if recurrence is None:
            recurrence = HistoricalProblemRecurrence(history)

        if baseline is None:
            baseline = HistoricalHealthBaseline(history)

        if deviation is None:
            deviation = HistoricalDeviationDetection(
                history,
                baseline=baseline,
            )

        if not isinstance(trends, HistoricalTrendIntelligence):
            raise ValueError(
                "trends must be a HistoricalTrendIntelligence."
            )

        if not isinstance(
            recurrence,
            HistoricalProblemRecurrence,
        ):
            raise ValueError(
                "recurrence must be a HistoricalProblemRecurrence."
            )

        if not isinstance(
            baseline,
            HistoricalHealthBaseline,
        ):
            raise ValueError(
                "baseline must be a HistoricalHealthBaseline."
            )

        if not isinstance(
            deviation,
            HistoricalDeviationDetection,
        ):
            raise ValueError(
                "deviation must be a HistoricalDeviationDetection."
            )

        self.history = history
        self.trends = trends
        self.recurrence = recurrence
        self.baseline = baseline
        self.deviation = deviation

    def machine_intelligence(self, machine_id):
        return {
            "machine_id": machine_id,
            "trend": deepcopy(
                self.trends.machine_trend(machine_id)
            ),
            "trend_state": self.trends.trend_state(machine_id),
            "recurrence": deepcopy(
                self.recurrence.projection(machine_id)
            ),
            "baseline": deepcopy(
                self.baseline.projection(machine_id)
            ),
        }

    def current_deviation(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "current_deviation requires a DiagnosticCase."
            )

        return deepcopy(
            self.deviation.detect(case)
        )

    def projection(self, machine_id, case=None):
        result = self.machine_intelligence(machine_id)

        if case is not None:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "case must be a DiagnosticCase."
                )

            if case.machine_id != machine_id:
                raise ValueError(
                    "case machine_id does not match machine_id."
                )

            result["deviation"] = self.current_deviation(case)

        return deepcopy(result)
