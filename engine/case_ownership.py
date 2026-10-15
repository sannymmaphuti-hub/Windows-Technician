from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.technician_identity import TechnicianIdentity


class CaseOwnership:
    """
    Canonical V1.0 case ownership model.

    Ownership identifies the technician currently responsible for
    technician-side case handling.

    The canonical DiagnosticCase and TechnicianWorkflow remain owned
    by their existing systems. This class only represents collaboration
    ownership.

    This class does not:
    - diagnose
    - investigate
    - change case lifecycle state
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, case, owner=None):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "case must be a DiagnosticCase."
            )

        if owner is not None and not isinstance(
            owner,
            TechnicianIdentity,
        ):
            raise ValueError(
                "owner must be a TechnicianIdentity or None."
            )

        self.case = case
        self.owner = owner

    @property
    def case_id(self):
        """Return the canonical case identifier."""
        return self.case.case_id

    @property
    def owner_id(self):
        """Return the current owner's identifier, if assigned."""
        if self.owner is None:
            return None

        return self.owner.technician_id

    @property
    def is_owned(self):
        """Return whether the case currently has an owner."""
        return self.owner is not None

    def assign(self, technician):
        """
        Assign the case to a technician.

        Assignment replaces the collaboration ownership reference only.
        The canonical DiagnosticCase is not mutated.
        """
        if not isinstance(
            technician,
            TechnicianIdentity,
        ):
            raise ValueError(
                "technician must be a TechnicianIdentity."
            )

        self.owner = technician

    def clear(self):
        """Remove the current collaboration owner."""
        self.owner = None

    def projection(self):
        """Return a defensive ownership projection."""
        return deepcopy(
            {
                "case_id": self.case_id,
                "owner": (
                    self.owner.projection()
                    if self.owner is not None
                    else None
                ),
                "owner_id": self.owner_id,
                "is_owned": self.is_owned,
            }
        )

    def __repr__(self):
        return (
            "CaseOwnership("
            f"case_id={self.case_id!r}, "
            f"owner_id={self.owner_id!r}, "
            f"is_owned={self.is_owned!r}"
            ")"
        )
