# ==========================================
# Windows Technician v0.9
# FLEET PROBLEM MODEL
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_problem import FleetProblem


class FleetProblemModel:

    SEVERITY_RANK = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetProblemModel requires a Fleet."
            )

        self.fleet = fleet

    def build(self, cases):
        """
        Aggregate existing machine-level DiagnosticCases into
        fleet-level problem representations.

        The model does not store or own the supplied cases.
        """

        if not isinstance(cases, list):
            raise ValueError(
                "cases must be a list."
            )

        grouped = {}

        for case in cases:

            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "Fleet problem analysis requires "
                    "DiagnosticCase objects."
                )

            machine_id = getattr(
                case,
                "machine_id",
                None,
            )

            if machine_id is None:
                continue

            if not self.fleet.contains_machine(machine_id):
                continue

            for finding in getattr(
                case,
                "findings",
                [],
            ):

                problem_type = getattr(
                    finding,
                    "finding_type",
                    None,
                )

                domain = getattr(
                    finding,
                    "category",
                    None,
                )

                severity = getattr(
                    finding,
                    "severity",
                    None,
                )

                if not problem_type:
                    continue

                if not domain:
                    continue

                if severity not in FleetProblem.SEVERITIES:
                    continue

                key = (
                    problem_type,
                    domain,
                )

                if key not in grouped:
                    grouped[key] = {
                        "severity": severity,
                        "machine_ids": [],
                    }

                current = grouped[key]

                if (
                    self.SEVERITY_RANK[severity]
                    > self.SEVERITY_RANK[
                        current["severity"]
                    ]
                ):
                    current["severity"] = severity

                if machine_id not in current["machine_ids"]:
                    current["machine_ids"].append(
                        machine_id
                    )

        problems = []

        for (
            problem_type,
            domain,
        ), data in grouped.items():

            problems.append(
                FleetProblem(
                    problem_type=problem_type,
                    domain=domain,
                    severity=data["severity"],
                    machine_ids=data["machine_ids"],
                )
            )

        return problems