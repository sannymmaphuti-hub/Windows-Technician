# ==========================================
# Windows Technician v0.9
# FLEET PROBLEM
# ==========================================


class FleetProblem:

    SEVERITIES = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    def __init__(
        self,
        problem_type,
        domain,
        severity,
        machine_ids,
    ):
        if not problem_type:
            raise ValueError(
                "problem_type is required."
            )

        if not domain:
            raise ValueError(
                "domain is required."
            )

        if severity not in self.SEVERITIES:
            raise ValueError(
                "severity must be LOW, MEDIUM, HIGH, or CRITICAL."
            )

        if not isinstance(machine_ids, list):
            raise ValueError(
                "machine_ids must be a list."
            )

        if not machine_ids:
            raise ValueError(
                "At least one affected machine is required."
            )

        if any(not machine_id for machine_id in machine_ids):
            raise ValueError(
                "machine_ids cannot contain empty values."
            )

        self.problem_type = problem_type
        self.domain = domain
        self.severity = severity
        self.machine_ids = list(
            dict.fromkeys(machine_ids)
        )

    @property
    def affected_machine_count(self):
        return len(self.machine_ids)

    @property
    def scope(self):
        if self.affected_machine_count == 1:
            return "ISOLATED"

        return "MULTI_MACHINE"

    def to_evidence(self):
        return {
            "problem_type": self.problem_type,
            "domain": self.domain,
            "severity": self.severity,
            "machine_ids": list(self.machine_ids),
            "affected_machine_count": (
                self.affected_machine_count
            ),
            "scope": self.scope,
        }
