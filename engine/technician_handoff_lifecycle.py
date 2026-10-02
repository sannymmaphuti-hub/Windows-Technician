from enum import Enum

from engine.technician_case_handoff import TechnicianCaseHandoff


class HandoffState(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class TechnicianHandoffLifecycle:

    def __init__(self, handoff):
        if not isinstance(handoff, TechnicianCaseHandoff):
            raise ValueError(
                "TechnicianHandoffLifecycle requires a "
                "TechnicianCaseHandoff."
            )

        self._handoff = handoff
        self._state = HandoffState.PENDING

    @property
    def handoff(self):
        return self._handoff

    @property
    def state(self):
        return self._state

    @property
    def is_terminal(self):
        return self._state in {
            HandoffState.REJECTED,
            HandoffState.COMPLETED,
        }

    def accept(self):
        if self._state is not HandoffState.PENDING:
            raise ValueError(
                "Only a pending handoff can be accepted."
            )

        self._state = HandoffState.ACCEPTED

    def reject(self):
        if self._state is not HandoffState.PENDING:
            raise ValueError(
                "Only a pending handoff can be rejected."
            )

        self._state = HandoffState.REJECTED

    def complete(self):
        if self._state is not HandoffState.ACCEPTED:
            raise ValueError(
                "Only an accepted handoff can be completed."
            )

        self._state = HandoffState.COMPLETED