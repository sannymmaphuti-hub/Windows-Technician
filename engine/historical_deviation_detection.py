from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_health_baseline import HistoricalHealthBaseline


class HistoricalDeviationDetection:
    """
    Canonical V1.0 historical deviation detection boundary.

    Compares the current DiagnosticCase against the machine's
    historical health baseline.

    This class does not:
    - mutate DiagnosticCase
    - mutate DiagnosticHistory
    - diagnose
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, history, baseline=None):
        if not isinstance(history, DiagnosticHistory):
            raise ValueError(
                "HistoricalDeviationDetection requires a DiagnosticHistory."
            )

        if baseline is None:
            baseline = HistoricalHealthBaseline(history)

        if not isinstance(baseline, HistoricalHealthBaseline):
            raise ValueError(
                "baseline must be a HistoricalHealthBaseline."
            )

        self.history = history
        self.baseline = baseline

    def detect(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "HistoricalDeviationDetection requires a DiagnosticCase."
            )

        machine_id = case.machine_id

        known_problems = set(
            self.baseline.known_problems(machine_id)
        )

        current_problems = set()

        for finding in case.findings:
            identity = self._problem_identity(finding)

            if identity is not None:
                current_problems.add(identity)

        new_problems = sorted(
            current_problems - known_problems
        )

        return {
            "machine_id": machine_id,
            "has_baseline": self.baseline.has_baseline(machine_id),
            "current_problem_count": len(current_problems),
            "known_problem_count": len(
                current_problems & known_problems
            ),
            "new_problem_count": len(new_problems),
            "new_problems": new_problems,
            "is_deviation": bool(new_problems),
        }

    def is_deviation(self, case):
        return self.detect(case)["is_deviation"]

    def new_problems(self, case):
        return deepcopy(
            self.detect(case)["new_problems"]
        )

    @staticmethod
    def _problem_identity(finding):
        if not isinstance(finding, dict):
            return None

        return (
            finding.get("finding")
            or finding.get("type")
            or finding.get("category")
        )
