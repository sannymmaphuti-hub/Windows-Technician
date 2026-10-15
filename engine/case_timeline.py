from copy import deepcopy

from engine.case_handoff import CaseHandoff
from engine.case_note import CaseNote
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


class CaseTimeline:
    """Read-oriented collaboration timeline for a canonical case."""

    def __init__(self, case_or_workflow):
        if isinstance(case_or_workflow, TechnicianWorkflow):
            self.workflow = case_or_workflow
            self.case = case_or_workflow.case
        elif isinstance(case_or_workflow, DiagnosticCase):
            self.workflow = None
            self.case = case_or_workflow
        else:
            raise ValueError(
                "CaseTimeline requires a DiagnosticCase "
                "or TechnicianWorkflow."
            )

        self._entries = []

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def machine_id(self):
        return self.case.machine_id

    @property
    def hostname(self):
        return self.case.hostname

    @property
    def history(self):
        if self.workflow is None:
            return ()

        return self.workflow.history

    @property
    def state(self):
        if self.workflow is None:
            return getattr(self.case, "lifecycle_state", None)

        return self.workflow.state

    @property
    def is_terminal(self):
        if self.workflow is None:
            return False

        return self.workflow.is_terminal

    @property
    def entries(self):
        return tuple(self._entries)

    def add_note(self, note):
        if not isinstance(note, CaseNote):
            raise ValueError("note must be a CaseNote.")

        if note.case_id != self.case_id:
            raise ValueError("Note belongs to a different case.")

        self._entries.append(note)

    def add_handoff(self, handoff):
        if not isinstance(handoff, CaseHandoff):
            raise ValueError("handoff must be a CaseHandoff.")

        if handoff.case_id != self.case_id:
            raise ValueError("Handoff belongs to a different case.")

        self._entries.append(handoff)

    def chronological_entries(self):
        return tuple(
            sorted(
                self._entries,
                key=lambda entry: entry.created_at,
            )
        )

    def projection(self):
        return deepcopy(
            {
                "case_id": self.case_id,
                "entries": [
                    entry.projection()
                    for entry in self.chronological_entries()
                ],
                "entry_count": len(self._entries),
            }
        )

    def __repr__(self):
        return (
            f"CaseTimeline("
            f"case_id={self.case_id!r}, "
            f"entry_count={len(self._entries)}"
            f")"
        )
