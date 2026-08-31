# ==========================================
# Windows Technician v0.3
# DIAGNOSTIC CONFIDENCE
# ==========================================


class ConfidenceCalculator:

    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0

    def calculate(self, evidence_strength):

        if evidence_strength < self.MIN_CONFIDENCE:
            return self.MIN_CONFIDENCE

        if evidence_strength > self.MAX_CONFIDENCE:
            return self.MAX_CONFIDENCE

        return float(evidence_strength)

    def classify(self, confidence):

        if confidence >= 0.80:
            return "HIGH"

        if confidence >= 0.50:
            return "MEDIUM"

        return "LOW"
