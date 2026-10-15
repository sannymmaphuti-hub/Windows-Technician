from collections import Counter
from copy import deepcopy

from engine.diagnostic_history import DiagnosticHistory


class HistoricalProblemRecurrence:
    """
    Canonical V1.0 historical problem recurrence boundary.

    Identifies recurring problems across historical DiagnosticCase
    snapshots.

    This class does not:
    - mutate DiagnosticCase
    - mutate DiagnosticHistory
    - diagnose live systems
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, history):
        if not isinstance(history, DiagnosticHistory):
            raise ValueError(
                "HistoricalProblemRecurrence requires a DiagnosticHistory."
            )

        self.history = history

    def machine_problems(self, machine_id):
        records = self.history.for_machine(machine_id)
        counts = Counter()

        for record in records:
            seen = set()

            for finding in record.findings:
                identity = self._problem_identity(finding)

                if identity is not None:
                    seen.add(identity)

            for identity in seen:
                counts[identity] += 1

        return [
            {
                "problem": problem,
                "occurrences": occurrences,
            }
            for problem, occurrences in counts.items()
        ]

    def recurring_problems(self, machine_id, minimum_occurrences=2):
        if not isinstance(minimum_occurrences, int):
            raise ValueError(
                "minimum_occurrences must be an integer."
            )

        if minimum_occurrences < 1:
            raise ValueError(
                "minimum_occurrences must be at least 1."
            )

        return [
            problem
            for problem in self.machine_problems(machine_id)
            if problem["occurrences"] >= minimum_occurrences
        ]

    def has_recurrence(self, machine_id):
        return bool(self.recurring_problems(machine_id))

    def recurrence_count(self, machine_id):
        return len(self.recurring_problems(machine_id))

    def projection(self, machine_id):
        problems = self.machine_problems(machine_id)
        recurring = self.recurring_problems(machine_id)

        return {
            "machine_id": machine_id,
            "problem_count": len(problems),
            "recurrence_count": len(recurring),
            "has_recurrence": bool(recurring),
            "problems": deepcopy(problems),
            "recurring_problems": deepcopy(recurring),
        }

    @staticmethod
    def _problem_identity(finding):
        if not isinstance(finding, dict):
            return None

        return (
            finding.get("finding")
            or finding.get("type")
            or finding.get("category")
        )
