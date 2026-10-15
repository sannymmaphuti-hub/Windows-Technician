from copy import deepcopy
from datetime import datetime, timezone

from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity
from engine.technician_workflow import TechnicianWorkflow


class CaseHandoff:
    """Collaboration handoff that never changes workflow lifecycle."""

    def __init__(
        self,
        ownership_or_workflow,
        to_technician=None,
        performed_by=None,
        reason=None,
        *,
        recipient=None,
    ):
        if recipient is not None:
            if to_technician is not None:
                raise ValueError(
                    "Provide either to_technician or recipient, not both."
                )
            to_technician = recipient

        self.created_at = datetime.now(timezone.utc)
        self.status = "PENDING"

        if isinstance(ownership_or_workflow, CaseOwnership):
            ownership = ownership_or_workflow

            if not isinstance(to_technician, TechnicianIdentity):
                raise ValueError(
                    "to_technician must be a TechnicianIdentity."
                )

            if not isinstance(performed_by, TechnicianIdentity):
                raise ValueError(
                    "performed_by must be a TechnicianIdentity."
                )

            if not ownership.is_owned:
                raise ValueError(
                    "A handoff requires an existing case owner."
                )

            if (
                ownership.owner.technician_id
                == to_technician.technician_id
            ):
                raise ValueError(
                    "Case cannot be handed off to the current owner."
                )

            if reason is not None:
                if not isinstance(reason, str) or not reason.strip():
                    raise ValueError(
                        "reason must be a non-empty string when provided."
                    )
                reason = reason.strip()

            self.ownership = ownership
            self.workflow = None
            self.from_technician = ownership.owner
            self.to_technician = to_technician
            self.performed_by = performed_by
            self._recipient = to_technician.technician_id
            self.reason = reason
            return

        if isinstance(ownership_or_workflow, TechnicianWorkflow):
            if not isinstance(to_technician, str) or not to_technician.strip():
                raise ValueError(
                    "recipient must be a non-empty technician identifier."
                )

            # In the legacy positional form, the third argument is
            # the reason rather than a TechnicianIdentity.
            if reason is None and isinstance(performed_by, str):
                reason = performed_by

            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(
                    "reason must be a non-empty string."
                )

            self.ownership = None
            self.workflow = ownership_or_workflow
            self.from_technician = None
            self.to_technician = None
            self.performed_by = None
            self._recipient = to_technician.strip()
            self.reason = reason.strip()
            return

        raise ValueError(
            "CaseHandoff requires a CaseOwnership or TechnicianWorkflow."
        )

    @property
    def case(self):
        if self.ownership is not None:
            return self.ownership.case

        return self.workflow.case

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
    def recipient(self):
        return self._recipient

    @property
    def from_technician_id(self):
        if self.from_technician is None:
            return None

        return self.from_technician.technician_id

    @property
    def to_technician_id(self):
        if self.to_technician is None:
            return self._recipient

        return self.to_technician.technician_id

    @property
    def performed_by_id(self):
        if self.performed_by is None:
            return None

        return self.performed_by.technician_id

    def accept(self):
        if self.status == "PENDING":
            self.status = "ACCEPTED"

    def decline(self):
        if self.status == "PENDING":
            self.status = "DECLINED"

    def apply(self):
        if self.ownership is None:
            if self.status == "PENDING":
                self.status = "ACCEPTED"
            return

        self.ownership.assign(self.to_technician)
        self.status = "ACCEPTED"

    def projection(self):
        return deepcopy(
            {
                "case_id": self.case_id,
                "from_technician": (
                    self.from_technician.projection()
                    if self.from_technician is not None
                    else None
                ),
                "from_technician_id": self.from_technician_id,
                "to_technician": (
                    self.to_technician.projection()
                    if self.to_technician is not None
                    else None
                ),
                "to_technician_id": self.to_technician_id,
                "performed_by": (
                    self.performed_by.projection()
                    if self.performed_by is not None
                    else None
                ),
                "performed_by_id": self.performed_by_id,
                "recipient": self.recipient,
                "reason": self.reason,
                "status": self.status,
                "created_at": self.created_at.isoformat(),
            }
        )

    def __repr__(self):
        return (
            f"CaseHandoff("
            f"case_id={self.case_id!r}, "
            f"recipient={self.recipient!r}, "
            f"status={self.status!r}"
            f")"
        )
