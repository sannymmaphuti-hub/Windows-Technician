# ==========================================
# Windows Technician v0.6
# REMEDIATION OPERATION CATALOG
# ==========================================

from engine.remediation_operation import RemediationOperation


class RemediationOperationCatalog:

    def __init__(self):
        self._operations = {
            "memory_review": RemediationOperation(
                operation_id="memory_review",
                description=(
                    "Review memory-intensive processes."
                ),
                handler=lambda: None,
            ),
        }

    def get(self, operation_id):
        return self._operations.get(operation_id)

    def get_operations(self):
        return self._operations.copy()

