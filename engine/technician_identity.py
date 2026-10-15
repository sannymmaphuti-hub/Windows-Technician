from copy import deepcopy


class TechnicianIdentity:
    """
    Canonical V1.0 technician identity.

    Represents the technician participating in collaboration and
    case-management operations.

    This class contains identity only. It does not own cases, mutate
    workflows, authorize remediation, execute remediation, or verify
    remediation.
    """

    VALID_ROLES = {
        "TECHNICIAN",
        "SENIOR_TECHNICIAN",
        "ADMINISTRATOR",
        "SUPERVISOR",
    }

    def __init__(self, technician_id, name, role="TECHNICIAN"):
        if not isinstance(technician_id, str) or not technician_id.strip():
            raise ValueError(
                "technician_id must be a non-empty string."
            )

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "name must be a non-empty string."
            )

        if not isinstance(role, str) or not role.strip():
            raise ValueError(
                "role must be a non-empty string."
            )

        normalized_role = role.strip().upper()

        if normalized_role not in self.VALID_ROLES:
            raise ValueError(
                f"Unsupported technician role: {role}"
            )

        self.technician_id = technician_id.strip()
        self.name = name.strip()
        self.role = normalized_role

    def projection(self):
        """Return a defensive technician identity projection."""
        return deepcopy(
            {
                "technician_id": self.technician_id,
                "name": self.name,
                "role": self.role,
            }
        )

    def __repr__(self):
        return (
            "TechnicianIdentity("
            f"technician_id={self.technician_id!r}, "
            f"name={self.name!r}, "
            f"role={self.role!r}"
            ")"
        )
