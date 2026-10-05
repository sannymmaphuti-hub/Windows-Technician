# ==========================================

# Windows Technician v0.8

# PROACTIVE CASE CREATION

# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.proactive_recommendation import ProactiveRecommendation

class ProactiveCaseCreator:


    def create(self, recommendation):

        if not isinstance(
            recommendation,
            ProactiveRecommendation,
        ):
            raise ValueError(
                "ProactiveCaseCreator requires a "
                "ProactiveRecommendation."
            )

        case = DiagnosticCase()

        # ==========================================
        # PROACTIVE CASE CONTEXT
        # ==========================================

        case.machine_id = recommendation.machine_id
        case.hostname = recommendation.hostname

        case.proactive_recommendation = recommendation
        case.proactive_alert = recommendation.alert

        return case

