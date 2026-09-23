# ==========================================
# Windows Technician v0.6
# STORAGE DIAGNOSTIC RULE
# ==========================================


from engine.rules.base_rule import BaseRule


class StorageFreeSpaceRule(BaseRule):

    name = "Storage Free Space Rule"
    category = "STORAGE"

    WARNING_THRESHOLD = 20
    CRITICAL_THRESHOLD = 10

    def evaluate(self, evidence):

        free_percent = evidence.get("free_percent")

        if free_percent is None:
            return None

        if free_percent < self.CRITICAL_THRESHOLD:

            return {
                "category": "STORAGE",
                "severity": "CRITICAL",
                "message": "Available storage space is critically low.",
                "confidence": 0.95
            }

        if free_percent <= self.WARNING_THRESHOLD:

            return {
                "category": "STORAGE",
                "severity": "WARNING",
                "message": "Available storage space is low.",
                "confidence": 0.85
            }

        return None
