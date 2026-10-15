from enum import Enum
import uuid
from datetime import datetime, timezone


class WorkflowState(Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    DIAGNOSED = "DIAGNOSED"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class TechnicianWorkflow:
    _TRANSITIONS = {
        WorkflowState.OPEN: {
            WorkflowState.INVESTIGATING,
            WorkflowState.ESCALATED,
        },
        WorkflowState.INVESTIGATING: {
            WorkflowState.DIAGNOSED,
            WorkflowState.ESCALATED,
        },
        WorkflowState.DIAGNOSED: {
            WorkflowState.ACTION_REQUIRED,
            WorkflowState.ESCALATED,
        },
        WorkflowState.ACTION_REQUIRED: {
            WorkflowState.REMEDIATING,
            WorkflowState.ESCALATED,
        },
        WorkflowState.REMEDIATING: {
            WorkflowState.VERIFYING,
            WorkflowState.INVESTIGATING,
            WorkflowState.ESCALATED,
        },
        WorkflowState.VERIFYING: {
            WorkflowState.RESOLVED,
            WorkflowState.REMEDIATING,
            WorkflowState.ESCALATED,
        },
        WorkflowState.RESOLVED: set(),
        WorkflowState.ESCALATED: set(),
    }

    def __init__(self, case):
        if case is None:
            raise ValueError(
                "TechnicianWorkflow requires a diagnostic case."
            )

        self.case = case
        self.workflow_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.state = WorkflowState.OPEN
        self._history = []

    @property
    def history(self):
        return list(self._history)

    @property
    def is_terminal(self):
        return self.state in {
            WorkflowState.RESOLVED,
            WorkflowState.ESCALATED,
        }

    def _transition_to(self, new_state):
        allowed_states = self._TRANSITIONS[self.state]

        if new_state not in allowed_states:
            raise ValueError(
                f"Invalid workflow transition: "
                f"{self.state.value} -> {new_state.value}."
            )

        previous_state = self.state
        self.state = new_state
        self._history.append((previous_state, new_state))

    def start_investigation(self):
        self._transition_to(WorkflowState.INVESTIGATING)

    def mark_diagnosed(self):
        self._transition_to(WorkflowState.DIAGNOSED)

    def require_action(self):
        self._transition_to(WorkflowState.ACTION_REQUIRED)

    def start_remediation(self):
        self._transition_to(WorkflowState.REMEDIATING)

    def start_verification(self):
        self._transition_to(WorkflowState.VERIFYING)

    def start_recovery_investigation(self):
        # Explicit recovery transition. No diagnosis, remediation,
        # execution, or retry is performed here.
        self._transition_to(WorkflowState.INVESTIGATING)

    def resolve(self):
        self._transition_to(WorkflowState.RESOLVED)

    def reopen(self):
        if self.state is not WorkflowState.RESOLVED:
            raise ValueError(
                "Only a resolved workflow can be reopened."
            )

        previous_state = self.state
        self.state = WorkflowState.INVESTIGATING
        self._history.append(
            (previous_state, WorkflowState.INVESTIGATING)
        )

    def escalate(self):
        self._transition_to(WorkflowState.ESCALATED)