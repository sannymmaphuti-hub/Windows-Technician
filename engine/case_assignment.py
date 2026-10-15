from copy import deepcopy

from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


class CaseAssignment:
    """
    Canonical V1.0 case assignment operation.

    Represents a controlled assignment of an existing case to a
    technician. The current owner is maintained by CaseOwnership.

    This class does not:
    - create DiagnosticCase objects
    - mutate DiagnosticCase lifecycle state
    - diagnose
    - investigate
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(
        self,
        case,
        assigned_to,
        assigned_by,
        reason=None,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "case must be a DiagnosticCase."
            )

        if not isinstance(
            assigned_to,
            TechnicianIdentity,
        ):
            raise ValueError(
                "assigned_to must be a TechnicianIdentity."
            )

        if not isinstance(
            assigned_by,
            TechnicianIdentity,
        ):
            raise ValueError(
                "assigned_by must be a TechnicianIdentity."
            )

        if reason is not None and not isinstance(reason, str):
            raise ValueError(
                "reason must be a string or None."
            )

        self.case = case
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.reason = reason.strip() if reason else None

    @property
    def case_id(self):
        """Return the canonical case identifier."""
        return self.case.case_id

    @property
    def assigned_to_id(self):
        """Return the destination technician identifier."""
        return self.assigned_to.technician_id

    @property
    def assigned_by_id(self):
        """Return the assigning technician identifier."""
        return self.assigned_by.technician_id

    def apply(self, ownership):
        """
        Apply this assignment to an existing CaseOwnership boundary.

        The assignment changes collaboration ownership only.
        """
        if not isinstance(
            ownership,
            CaseOwnership,
        ):
            raise ValueError(
                "ownership must be a CaseOwnership."
            )

        if ownership.case is not self.case:
            raise ValueError(
                "ownership must reference the same canonical case."
            )

        ownership.assign(self.assigned_to)

    def projection(self):
        """Return a defensive assignment projection."""
        return deepcopy(
            {
                "case_id": self.case_id,
                "assigned_to": self.assigned_to.projection(),
                "assigned_to_id": self.assigned_to_id,
                "assigned_by": self.assigned_by.projection(),
                "assigned_by_id": self.assigned_by_id,
                "reason": self.reason,
            }
        )

    def __repr__(self):
        return (
            "CaseAssignment("
            f"case_id={self.case_id!r}, "
            f"assigned_to_id={self.assigned_to_id!r}, "
            f"assigned_by_id={self.assigned_by_id!r}"
            ")"
        )
