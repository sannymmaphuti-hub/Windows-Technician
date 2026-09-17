# ==========================================
# Windows Technician v0.5
# REMEDIATION OPERATION SELECTOR
# ==========================================


class RemediationOperationSelector:

    OPERATION_MAP = {
        ("MEMORY", "WARNING"): "memory_review",
    }

    def select(self, action):

        if action is None:
            return None

        key = (
            action.category,
            action.severity,
        )

        return self.OPERATION_MAP.get(key)
