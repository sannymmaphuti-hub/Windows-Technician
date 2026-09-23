# ==========================================
# Windows Technician v0.6
# GPU DIAGNOSTIC RULE
# ==========================================

from engine.rules.base_rule import BaseRule


class GPUStatusRule(BaseRule):

    name = "GPU Status Rule"
    category = "GPU"

    def evaluate(self, evidence):

        gpus = evidence.get("gpus")

        if gpus is None:
            return None

        if not gpus:

            return {
                "category": "GPU",
                "severity": "WARNING",
                "message": "No GPU was detected.",
                "confidence": 0.85
            }

        unhealthy_gpus = [
            gpu
            for gpu in gpus
            if gpu.get("status") not in ("OK", "NORMAL")
        ]

        if unhealthy_gpus:

            gpu = unhealthy_gpus[0]

            return {
                "category": "GPU",
                "severity": "WARNING",
                "message": (
                    f"{gpu.get('name', 'Unknown GPU')} "
                    f"reported status {gpu.get('status', 'UNKNOWN')}."
                ),
                "confidence": 0.90
            }

        return None
