import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@dataclass(frozen=True)
class TechnicianCaseNote:
    note_id: str
    text: str
    created_at: datetime
    workflow_state: WorkflowState


class TechnicianCaseNotes:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseNotes requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._notes = []

    @property
    def workflow(self):
        return self._workflow

    @property
    def notes(self):
        return list(self._notes)

    def add_note(self, text, workflow_state=None):
        if not isinstance(text, str):
            raise ValueError(
                "Technician case note text must be a string."
            )

        if not text.strip():
            raise ValueError(
                "Technician case note text cannot be empty."
            )

        if workflow_state is None:
            workflow_state = self._workflow.state

        if not isinstance(workflow_state, WorkflowState):
            raise ValueError(
                "Technician case note requires a valid workflow state."
            )

        note = TechnicianCaseNote(
            note_id=str(uuid.uuid4()),
            text=text,
            created_at=datetime.now(timezone.utc),
            workflow_state=workflow_state,
        )

        self._notes.append(note)

        return note