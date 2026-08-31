# ==========================================
# Windows Technician v0.3
# BASE DIAGNOSTIC RULE
# ==========================================


class BaseRule:

    name = "Base Rule"
    category = "GENERAL"

    def evaluate(self, evidence):

        raise NotImplementedError(
            "Diagnostic rules must implement evaluate()."
        )
