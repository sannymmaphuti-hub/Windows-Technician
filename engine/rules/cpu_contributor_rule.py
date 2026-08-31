
# ==========================================
# Windows Technician v0.3
# CPU CONTRIBUTOR DIAGNOSTIC RULE
# ==========================================


from engine.rules.base_rule import BaseRule


class CPUContributorRule(BaseRule):

    name = "CPU Contributor Rule"
    category = "CPU"

    WARNING_CPU_THRESHOLD = 80
    CRITICAL_CPU_THRESHOLD = 95

    def evaluate(self, evidence):

        usage_percent = evidence.get("usage_percent")
        top_processes = evidence.get("top_processes")

        if usage_percent is None:
            return None

        if not top_processes:
            return None

        highest_process = top_processes[0]

        process_name = highest_process.get("name")
        process_cpu = highest_process.get("cpu_percent")

        if process_name is None or process_cpu is None:
            return None

        # Overall CPU is normal.
        # There is no significant CPU problem to attribute.
        if usage_percent < self.WARNING_CPU_THRESHOLD:
            return None

        # Overall CPU is critical.
        if usage_percent >= self.CRITICAL_CPU_THRESHOLD:

            return {
                "category": "CPU",
                "severity": "CRITICAL",
                "message": (
                    f"{process_name} is the highest CPU-consuming process "
                    f"at {process_cpu:.2f}%."
                ),
                "confidence": 0.95
            }

        # Overall CPU is high but not critical.
        return {
            "category": "CPU",
            "severity": "WARNING",
            "message": (
                f"{process_name} is the highest CPU-consuming process "
                f"at {process_cpu:.2f}%."
            ),
            "confidence": 0.90
        }
