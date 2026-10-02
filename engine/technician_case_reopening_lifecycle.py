from enum import Enum

from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)


class ReopeningState(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class TechnicianCaseReopeningLifecycle:

    def __init__(self, reopening):
        if not isinstance(
            reopening,
            TechnicianCaseReopening,
        ):
            raise ValueError(
                "TechnicianCaseReopeningLifecycle requires a "
                "TechnicianCaseReopening."
            )

        self._reopening = reopening
        self._state = ReopeningState.PENDING

    @property
    def reopening(self):
        return self._reopening

    @property
    def state(self):
        return self._state

    @property
    def is_terminal(self):
        return self._state in {
            ReopeningState.REJECTED,
            ReopeningState.COMPLETED,
        }

    def accept(self):
        if self._state is not ReopeningState.PENDING:
            raise ValueError(
                "Only a pending reopening can be accepted."
            )

        self._state = ReopeningState.ACCEPTED

    def reject(self):
        if self._state is not ReopeningState.PENDING:
            raise ValueError(
                "Only a pending reopening can be rejected."
            )

        self._state = ReopeningState.REJECTED

    def complete(self):
        if self._state is not ReopeningState.ACCEPTED:
            raise ValueError(
                "Only an accepted reopening can be completed."
            )

        self._state = ReopeningState.COMPLETED