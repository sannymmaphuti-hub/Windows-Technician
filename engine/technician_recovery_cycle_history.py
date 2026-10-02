from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianRecoveryCycleHistory:

    def __init__(self, workflow):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianRecoveryCycleHistory requires a "
                "TechnicianWorkflow."
            )

        self._workflow = workflow
        self._cycles = [
            TechnicianRecoveryCycle(
                workflow,
                cycle_number=0,
            )
        ]

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycles(self):
        return list(self._cycles)

    @property
    def cycle_count(self):
        return len(self._cycles)

    @property
    def latest_cycle(self):
        return self._cycles[-1]

    def record_cycle(self, cycle):
        if not isinstance(
            cycle,
            TechnicianRecoveryCycle,
        ):
            raise ValueError(
                "Recovery cycle history requires a "
                "TechnicianRecoveryCycle."
            )

        if cycle.workflow is not self._workflow:
            raise ValueError(
                "Recovery cycle belongs to a different workflow."
            )

        if cycle in self._cycles:
            raise ValueError(
                "Recovery cycle has already been recorded."
            )

        expected_number = (
            self._cycles[-1].cycle_number + 1
        )

        if cycle.cycle_number != expected_number:
            raise ValueError(
                "Recovery cycle number must be sequential."
            )

        self._cycles.append(cycle)

        return cycle