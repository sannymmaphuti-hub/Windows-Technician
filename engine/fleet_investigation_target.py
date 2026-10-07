class FleetInvestigationTarget:

    def __init__(
        self,
        machine_id,
        problem_type,
        domain,
        reason,
    ):
        if not isinstance(machine_id, str) or not machine_id.strip():
            raise ValueError("machine_id is required")

        if not isinstance(problem_type, str) or not problem_type.strip():
            raise ValueError("problem_type is required")

        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain is required")

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason is required")

        self.machine_id = machine_id
        self.problem_type = problem_type
        self.domain = domain
        self.reason = reason

    def to_evidence(self):
        return {
            "machine_id": self.machine_id,
            "problem_type": self.problem_type,
            "domain": self.domain,
            "reason": self.reason,
        }
