# ==========================================
# WINDOWS TECHNICIAN v0.1
# CPU DIAGNOSTIC RULE
# ==========================================


from engine.rules.base_rule import BaseRule


class CPUUsageRule(BaseRule):

    name = "CPU Usage Rule"
    category = "CPU"

    WARNING_THRESHOLD = 80
    CRITICAL_THRESHOLD = 95

    def evaluate(self, evidence):

        usage_percent = evidence.get("usage_percent")

        if usage_percent is None:
            return None

        if usage_percent >= self.CRITICAL_THRESHOLD:

            return {
                "category": "CPU",
                "severity": "CRITICAL",
                "message": "Critically high CPU utilization.",
                "confidence": 0.95
            }

        if usage_percent >= self.WARNING_THRESHOLD:

            return {
                "category": "CPU",
                "severity": "WARNING",
                "message": "Elevated CPU utilization.",
                "confidence": 0.85
            }

        return None