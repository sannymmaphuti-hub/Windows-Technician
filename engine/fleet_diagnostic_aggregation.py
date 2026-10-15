from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet


class FleetDiagnosticAggregation:
    """
    V1.0 read-only aggregation of canonical DiagnosticCase
    diagnostic data across Fleet membership.

    This class observes existing DiagnosticCase objects. It does
    not create, mutate, diagnose, authorize, remediate, verify,
    or recover cases.
    """

    def __init__(self, fleet, cases=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetDiagnosticAggregation requires a Fleet."
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
                    "FleetDiagnosticAggregation requires "
                    "DiagnosticCase objects."
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
    def affected_machine_ids(self):
        return list(
            dict.fromkeys(
                case.machine_id
                for case in self._fleet_cases()
            )
        )

    @property
    def affected_machine_count(self):
        return len(self.affected_machine_ids)

    def observation_count(self):
        return sum(
            len(case.observations)
            for case in self._fleet_cases()
        )

    def signal_count(self):
        return sum(
            len(case.signals)
            for case in self._fleet_cases()
        )

    def finding_count(self):
        return sum(
            len(case.findings)
            for case in self._fleet_cases()
        )

    def correlation_count(self):
        return sum(
            len(case.correlations)
            for case in self._fleet_cases()
        )

    def root_cause_count(self):
        return sum(
            len(case.root_causes)
            for case in self._fleet_cases()
        )

    def recommendation_count(self):
        return sum(
            len(case.recommendations)
            for case in self._fleet_cases()
        )

    def case_diagnostic_surface(self):
        """
        Return a defensive diagnostic snapshot for each fleet case.

        The underlying DiagnosticCase remains the source of truth.
        """
        return deepcopy(
            [
                {
                    "case_id": case.case_id,
                    "machine_id": case.machine_id,
                    "hostname": getattr(
                        case,
                        "hostname",
                        None,
                    ),
                    "lifecycle_state": case.lifecycle_state,
                    "diagnostic_completeness": (
                        case.diagnostic_completeness
                    ),
                    "status": case.status,
                    "observation_count": len(
                        case.observations
                    ),
                    "signal_count": len(
                        case.signals
                    ),
                    "finding_count": len(
                        case.findings
                    ),
                    "correlation_count": len(
                        case.correlations
                    ),
                    "root_cause_count": len(
                        case.root_causes
                    ),
                    "recommendation_count": len(
                        case.recommendations
                    ),
                }
                for case in self._fleet_cases()
            ]
        )

    def projection(self):
        """
        Return the canonical fleet diagnostic aggregation.

        This is a read-only projection and does not alter any
        DiagnosticCase or Fleet object.
        """
        return {
            "case_count": self.case_count,
            "affected_machine_count": (
                self.affected_machine_count
            ),
            "affected_machine_ids": deepcopy(
                self.affected_machine_ids
            ),
            "observation_count": self.observation_count(),
            "signal_count": self.signal_count(),
            "finding_count": self.finding_count(),
            "correlation_count": self.correlation_count(),
            "root_cause_count": self.root_cause_count(),
            "recommendation_count": (
                self.recommendation_count()
            ),
            "cases": self.case_diagnostic_surface(),
        }

    def _fleet_cases(self):
        fleet_machine_ids = set(
            self.fleet.machine_ids
        )

        return [
            case
            for case in self._cases
            if getattr(case, "machine_id", None)
            in fleet_machine_ids
        ]
