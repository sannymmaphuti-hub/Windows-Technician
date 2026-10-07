from engine.fleet_recommendation_context import FleetRecommendationContext
from engine.recommendation import Recommendation


class FleetRecommendationIntelligence:
    """
    Generates technician-facing recommendations from fleet
    investigation context.

    This layer adapts fleet reasoning into the canonical
    Recommendation model. It does not authorize, execute,
    verify, or remediate anything.
    """

    def generate(self, context):
        if not isinstance(context, FleetRecommendationContext):
            raise ValueError(
                "context must be a FleetRecommendationContext."
            )

        if context.primary_cause is None:
            return []

        if not context.evaluations:
            return []

        supported = any(
            evaluation.candidate is context.primary_cause
            and evaluation.assessment
            in {"SUPPORTED", "STRONGLY_SUPPORTED"}
            for evaluation in context.evaluations
        )

        if not supported:
            return []

        if context.pattern_type == "WIDESPREAD":
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        return [
            Recommendation(
                recommendation_type="fleet_investigation",
                category=context.pattern.domain,
                priority=priority,
                description=(
                    f"Investigate the {context.pattern.problem_type} "
                    f"condition across the affected machines."
                ),
                rationale=(
                    f"The condition affects "
                    f"{context.affected_machine_count} of "
                    f"{context.fleet_machine_count} machines "
                    f"({context.affected_machine_ratio:.0%}) and "
                    f"existing root-cause evidence supports "
                    f"further investigation."
                ),
            )
        ]
