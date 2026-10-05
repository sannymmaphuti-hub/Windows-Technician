from engine.diagnostic_case import DiagnosticCase


class TechnicianNotes:

    def __init__(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "TechnicianNotes requires a DiagnosticCase."
            )

        self.case = case
        self._notes = []

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def notes(self):
        return list(self._notes)

    @property
    def note_count(self):
        return len(self._notes)

    def add_note(self, note):
        if not isinstance(note, str):
            raise ValueError(
                "TechnicianNotes requires string notes."
            )

        if not note.strip():
            raise ValueError(
                "TechnicianNotes cannot contain empty notes."
            )

        self._notes.append(note)