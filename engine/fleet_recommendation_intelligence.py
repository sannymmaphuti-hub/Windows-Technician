from copy import deepcopy

from engine.fleet_recommendation_context import FleetRecommendationContext
from engine.recommendation import Recommendation
from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetRecommendationIntelligence:
    """
    Canonical V1.0 fleet recommendation intelligence.

    Generates recommendations from validated fleet investigation
    context and aggregates recommendations already present on
    canonical DiagnosticCase objects.

    This layer does not authorize, execute, verify, or remediate.
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

        priority = (
            "HIGH"
            if context.pattern_type == "WIDESPREAD"
            else "MEDIUM"
        )

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

    def _validate_fleet(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "fleet must be a Fleet."
            )

    def _fleet_cases(self, fleet, cases):
        self._validate_fleet(fleet)

        if cases is None:
            cases = []

        if not isinstance(cases, (list, tuple)):
            raise ValueError(
                "cases must be a list or tuple."
            )

        for case in cases:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "cases must contain DiagnosticCase objects."
                )

        aggregation = FleetCaseAggregation(
            fleet,
            cases,
        )

        return aggregation.cases

    @staticmethod
    def _value(recommendation, *names):
        if isinstance(recommendation, dict):
            for name in names:
                value = recommendation.get(name)
                if value is not None:
                    return value
            return None

        for name in names:
            value = getattr(
                recommendation,
                name,
                None,
            )
            if value is not None:
                return value

        return None

    @classmethod
    def _recommendation_key(cls, recommendation):
        value = cls._value(
            recommendation,
            "recommendation_id",
            "recommendation_type",
            "type",
            "code",
            "name",
            "category",
            "description",
        )

        if value is not None:
            if hasattr(value, "value"):
                value = value.value
            return str(value)

        if isinstance(recommendation, dict):
            return str(
                sorted(
                    recommendation.items()
                )
            )

        return str(recommendation)

    @classmethod
    def _priority(cls, recommendation):
        value = cls._value(
            recommendation,
            "priority",
            "severity",
            "level",
        )

        if value is None:
            return "UNKNOWN"

        if hasattr(value, "value"):
            value = value.value

        return str(value).upper()

    def recommendation_occurrences(self, fleet, cases=None):
        occurrences = {}

        for case in self._fleet_cases(fleet, cases):
            for recommendation in getattr(
                case,
                "recommendations",
                [],
            ):
                key = self._recommendation_key(
                    recommendation
                )

                if key not in occurrences:
                    occurrences[key] = {
                        "recommendation": deepcopy(
                            recommendation
                        ),
                        "machine_ids": [],
                        "case_ids": [],
                        "occurrence_count": 0,
                        "priority_counts": {},
                    }

                entry = occurrences[key]
                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(
                        case.machine_id
                    )

                if case.case_id not in entry["case_ids"]:
                    entry["case_ids"].append(
                        case.case_id
                    )

                priority = self._priority(
                    recommendation
                )

                entry["priority_counts"][priority] = (
                    entry["priority_counts"].get(
                        priority,
                        0,
                    ) + 1
                )

        return deepcopy(occurrences)

    def recurring_recommendations(self, fleet, cases=None):
        return {
            key: value
            for key, value in self.recommendation_occurrences(
                fleet,
                cases,
            ).items()
            if len(value["machine_ids"]) > 1
        }

    def affected_machine_ids(self, fleet, cases=None):
        result = []

        for case in self._fleet_cases(fleet, cases):
            if getattr(
                case,
                "recommendations",
                [],
            ):
                if case.machine_id not in result:
                    result.append(case.machine_id)

        return result

    def recommendation_priority_counts(
        self,
        fleet,
        cases=None,
    ):
        counts = {}

        for case in self._fleet_cases(fleet, cases):
            for recommendation in getattr(
                case,
                "recommendations",
                [],
            ):
                priority = self._priority(
                    recommendation
                )

                counts[priority] = (
                    counts.get(priority, 0) + 1
                )

        return counts

    def machine_recommendations(self, fleet, cases=None):
        result = {}

        for case in self._fleet_cases(fleet, cases):
            machine_id = case.machine_id
            result.setdefault(machine_id, [])

            for recommendation in getattr(
                case,
                "recommendations",
                [],
            ):
                result[machine_id].append(
                    {
                        "recommendation_key": (
                            self._recommendation_key(
                                recommendation
                            )
                        ),
                        "priority": self._priority(
                            recommendation
                        ),
                        "case_id": case.case_id,
                    }
                )

        return deepcopy(result)

    def summary(self, fleet, cases=None):
        occurrences = self.recommendation_occurrences(
            fleet,
            cases,
        )

        return {
            "unique_recommendation_count": len(
                occurrences
            ),
            "total_recommendation_occurrences": sum(
                entry["occurrence_count"]
                for entry in occurrences.values()
            ),
            "recurring_recommendation_count": len(
                self.recurring_recommendations(
                    fleet,
                    cases,
                )
            ),
            "affected_machine_count": len(
                self.affected_machine_ids(
                    fleet,
                    cases,
                )
            ),
            "priority_counts": (
                self.recommendation_priority_counts(
                    fleet,
                    cases,
                )
            ),
        }

    def projection(self, fleet, cases=None):
        self._validate_fleet(fleet)

        return {
            "fleet": {
                "fleet_id": fleet.fleet_id,
                "name": fleet.name,
            },
            "summary": self.summary(
                fleet,
                cases,
            ),
            "affected_machine_ids": (
                self.affected_machine_ids(
                    fleet,
                    cases,
                )
            ),
            "recommendation_priority_counts": (
                self.recommendation_priority_counts(
                    fleet,
                    cases,
                )
            ),
            "recommendation_occurrences": (
                self.recommendation_occurrences(
                    fleet,
                    cases,
                )
            ),
            "recurring_recommendations": (
                self.recurring_recommendations(
                    fleet,
                    cases,
                )
            ),
            "machine_recommendations": (
                self.machine_recommendations(
                    fleet,
                    cases,
                )
            ),
        }
