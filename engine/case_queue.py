# ==========================================
# Windows Technician v0.8
# CASE QUEUE
# ==========================================

from engine.diagnostic_case import DiagnosticCase


class CaseQueue:

    def __init__(self):
        self.cases = []

    def add_case(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "CaseQueue requires a DiagnosticCase."
            )

        self.cases.append(case)

    @property
    def case_count(self):
        return len(self.cases)

    def for_machine(self, machine_id):
        return [
            case
            for case in self.cases
            if case.machine_id == machine_id
        ]

    def by_lifecycle_state(self, lifecycle_state):
        return [
            case
            for case in self.cases
            if case.lifecycle_state == lifecycle_state
        ]

    @property
    def open_cases(self):
        return self.by_lifecycle_state("OPEN")

    @property
    def active_cases(self):
        active_states = {
            "OPEN",
            "INVESTIGATING",
            "DIAGNOSED",
            "ACTION_REQUIRED",
            "REMEDIATING",
            "VERIFYING",
        }

        return [
            case
            for case in self.cases
            if case.lifecycle_state in active_states
        ]