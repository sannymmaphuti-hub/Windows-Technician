from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


class CaseNote:
    VALID_ACTIVITY_TYPES = {
        "NOTE",
        "INVESTIGATION",
        "HANDOFF",
        "STATUS_UPDATE",
        "CUSTOMER_UPDATE",
    }

    def __init__(
        self,
        case,
        technician,
        content,
        activity_type="NOTE",
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError("case must be a DiagnosticCase.")

        if not isinstance(technician, TechnicianIdentity):
            raise ValueError(
                "technician must be a TechnicianIdentity."
            )

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "content must be a non-empty string."
            )

        normalized_type = str(activity_type).strip().upper()

        if normalized_type not in self.VALID_ACTIVITY_TYPES:
            raise ValueError(
                f"Unsupported activity type: {activity_type!r}."
            )

        self.note_id = str(uuid4())
        self.case = case
        self.technician = technician
        self.content = content.strip()
        self.activity_type = normalized_type
        self.created_at = datetime.now(timezone.utc)

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def technician_id(self):
        return self.technician.technician_id

    def projection(self):
        return deepcopy(
            {
                "note_id": self.note_id,
                "case_id": self.case_id,
                "technician_id": self.technician.technician_id,
                "technician_name": self.technician.name,
                "activity_type": self.activity_type,
                "content": self.content,
                "created_at": self.created_at.isoformat(),
            }
        )

    def __repr__(self):
        return (
            f"CaseNote("
            f"note_id={self.note_id!r}, "
            f"case_id={self.case_id!r}, "
            f"technician_id={self.technician_id!r}, "
            f"activity_type={self.activity_type!r}"
            f")"
        )
