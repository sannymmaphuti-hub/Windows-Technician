# ==========================================
# Windows Technician v0.5
# MEMORY DIAGNOSTIC RULE
# ==========================================


from engine.rules.base_rule import BaseRule


class MemoryUsageRule(BaseRule):

    name = "Memory Usage Rule"
    category = "MEMORY"

    WARNING_THRESHOLD = 80
    CRITICAL_THRESHOLD = 95

    def evaluate(self, evidence):

        usage_percent = evidence.get("usage_percent")

        if usage_percent is None:
            return None

        if usage_percent >= self.CRITICAL_THRESHOLD:

            return {
                "category": "MEMORY",
                "severity": "CRITICAL",
                "message": "Critically high memory usage.",
                "confidence": 0.95
            }

        if usage_percent >= self.WARNING_THRESHOLD:

            return {
                "category": "MEMORY",
                "severity": "WARNING",
                "message": "High memory usage.",
                "confidence": 0.85
            }

        return None

