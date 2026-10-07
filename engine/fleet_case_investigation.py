from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_investigation_target import FleetInvestigationTarget


class FleetCaseInvestigation:

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError("fleet must be a Fleet")

        self.fleet = fleet

    def resolve_cases(self, targets, cases):
        if not isinstance(targets, list):
            raise ValueError("targets must be a list")

        if not isinstance(cases, list):
            raise ValueError("cases must be a list")

        for target in targets:
            if not isinstance(target, FleetInvestigationTarget):
                raise ValueError(
                    "targets must contain FleetInvestigationTarget objects"
                )

        for case in cases:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "cases must contain DiagnosticCase objects"
                )

        cases_by_machine = {}

        for case in cases:
            machine_id = getattr(case, "machine_id", None)

            if machine_id is None:
                continue

            cases_by_machine[machine_id] = case

        resolved = []

        for target in targets:
            case = cases_by_machine.get(target.machine_id)

            resolved.append(
                {
                    "target": target,
                    "case": case,
                }
            )

        return resolved
