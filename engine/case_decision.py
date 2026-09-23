# ==========================================
# Windows Technician v0.6
# CASE DECISION
# ==========================================

from copy import deepcopy


class CaseDecision:

    def __init__(self, case):

        self.case = case
        self.result = {}

    def evaluate(self):

        primary_root_cause = self.case.primary_root_cause

        if primary_root_cause is None:
            self.result = {}
            return self.result

        cause = primary_root_cause.get("cause")
        severity = primary_root_cause.get("severity")
        confidence = primary_root_cause.get("confidence")

        # ==========================================
        # ACTION DECISION
        # ==========================================

        if severity == "HIGH":

            if confidence is not None and confidence >= 0.8:
                action = "IMMEDIATE_ATTENTION"
            else:
                action = "REVIEW_RECOMMENDED"

        elif severity == "MEDIUM":

            action = "REVIEW_RECOMMENDED"

        elif severity == "LOW":

            action = "MONITOR"

        else:

            action = None

        # ==========================================
        # EXPLANATION DECISION
        # ==========================================

        if confidence is not None:
            confidence_percent = int(confidence * 100)
            confidence_text = f"{confidence_percent}% confidence"
        else:
            confidence_text = "unknown confidence"

        if action == "IMMEDIATE_ATTENTION":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. Immediate attention is required."
            )

        elif action == "REVIEW_RECOMMENDED":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. Review is recommended."
            )

        elif action == "MONITOR":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. Monitoring is recommended."
            )

        else:

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. No immediate action was determined."
            )

        # ==========================================
        # PRIORITY DECISION
        # ==========================================

        if action == "IMMEDIATE_ATTENTION":

            priority = "CRITICAL"

        elif action == "REVIEW_RECOMMENDED":

            priority = "REVIEW"

        elif action == "MONITOR":

            priority = "MONITOR"

        else:

            priority = None

        # ==========================================
        # RECOMMENDATION DECISION
        # ==========================================

        if self.case.recommendations:

            recommendations = deepcopy(
                self.case.recommendations
            )

            if len(recommendations) == 1:
                recommendation = recommendations[0]

            else:
                recommendation = recommendations

        elif cause == "Memory pressure":

            recommendation = (
                "Investigate memory-consuming processes"
            )

        else:

            recommendation = (
                "Investigate the primary root cause"
            )

        # ==========================================
        # EXPLANATION DECISION
        # ==========================================

        if confidence is None:

            confidence_text = "unknown confidence"

        else:

            confidence_text = f"{int(confidence * 100)}% confidence"


        if action == "IMMEDIATE_ATTENTION":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. "
                "Immediate attention is required."
            )

        elif action == "REVIEW_RECOMMENDED":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. "
                "Review is recommended."
            )

        elif action == "MONITOR":

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. "
                "Monitoring is recommended."
            )

        else:

            explanation = (
                f"{cause} was identified with {severity} severity "
                f"and {confidence_text}. "
                "No immediate action was determined."
            )

        # ==========================================
        # FINAL RESULT
        # ==========================================

        self.result = {
            "primary_root_cause": deepcopy(
                primary_root_cause
            ),
            "cause": cause,
            "severity": severity,
            "confidence": confidence,
            "action": action,
            "priority": priority,
            "recommendation": recommendation,
            "explanation": explanation

        }

        return self.result
