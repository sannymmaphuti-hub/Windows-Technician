# ==========================================
# WINDOWS TECHNICIAN v0.2
# BASE DIAGNOSTIC RULE
# ==========================================


class BaseRule:

    name = "Base Rule"
    category = "GENERAL"

    def evaluate(self, evidence):

        raise NotImplementedError(
            "Diagnostic rules must implement evaluate()."
        )
