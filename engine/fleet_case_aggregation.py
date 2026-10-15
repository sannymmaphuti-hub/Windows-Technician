from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet


class FleetCaseAggregation:
    """
    Read-only fleet case aggregation.

    Projects DiagnosticCase objects whose machine identity belongs
    to the canonical Fleet membership.

    FleetCaseAggregation does not own, create, mutate, diagnose,
    authorize, remediate, or verify cases.
    """

    _ACTIVE_STATES = {
        "OPEN",
        "INVESTIGATING",
        "DIAGNOSED",
        "ACTION_REQUIRED",
        "REMEDIATING",
        "VERIFYING",
    }

    _TERMINAL_STATES = {
        "RESOLVED",
        "CLOSED",
    }

    def __init__(self, fleet, cases=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetCaseAggregation requires a Fleet."
            )

        if cases is None:
            cases = []

        if not isinstance(cases, (list, tuple)):
            raise ValueError(
                "cases must be a list or tuple."
            )

        for case in cases:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "FleetCaseAggregation requires DiagnosticCase objects."
                )

        self.fleet = fleet
        self._cases = list(cases)

    @property
    def cases(self):
        return list(self._fleet_cases())

    @property
    def case_count(self):
        return len(self.cases)

    @property
    def active_case_count(self):
        return len(self.active_cases())

    @property
    def unresolved_case_count(self):
        return len(self.unresolved_cases())

    def active_cases(self):
        return [
            self._case_snapshot(case)
            for case in self._fleet_cases()
            if case.lifecycle_state in self._ACTIVE_STATES
        ]

    def unresolved_cases(self):
        return [
            self._case_snapshot(case)
            for case in self._fleet_cases()
            if case.lifecycle_state not in self._TERMINAL_STATES
        ]

    def cases_by_machine(self):
        result = {}

        for case in self._fleet_cases():
            machine_id = case.machine_id
            result.setdefault(machine_id, [])
            result[machine_id].append(
                self._case_snapshot(case)
            )

        return deepcopy(result)

    def state_counts(self):
        counts = {}

        for case in self._fleet_cases():
            state = case.lifecycle_state
            counts[state] = counts.get(state, 0) + 1

        return counts

    def affected_machine_ids(self):
        return list(
            dict.fromkeys(
                case.machine_id
                for case in self._fleet_cases()
            )
        )

    def projection(self):
        return {
            "case_count": self.case_count,
            "active_case_count": self.active_case_count,
            "unresolved_case_count": self.unresolved_case_count,
            "affected_machine_ids": self.affected_machine_ids(),
            "state_counts": self.state_counts(),
            "active_cases": self.active_cases(),
            "unresolved_cases": self.unresolved_cases(),
            "cases_by_machine": self.cases_by_machine(),
        }

    def _fleet_cases(self):
        fleet_machine_ids = set(self.fleet.machine_ids)

        return [
            case
            for case in self._cases
            if case.machine_id in fleet_machine_ids
        ]

    @staticmethod
    def _case_snapshot(case):
        return {
            "case_id": case.case_id,
            "machine_id": case.machine_id,
            "hostname": getattr(
                case,
                "hostname",
                None,
            ),
            "lifecycle_state": case.lifecycle_state,
        }
