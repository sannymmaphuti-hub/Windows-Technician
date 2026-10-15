from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetPrioritization:
    """
    Canonical V1.0 fleet prioritization intelligence.

    Ranks existing recommendations across a Fleet according to
    deterministic, explainable impact factors.

    This layer does not:
    - diagnose machines
    - create findings
    - infer root causes
    - create recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    - mutate DiagnosticCase objects
    """

    PRIORITY_WEIGHTS = {
        "LOW": 10,
        "MEDIUM": 30,
        "HIGH": 60,
        "CRITICAL": 100,
        "UNKNOWN": 0,
    }

    def __init__(self, fleet, cases=None):
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

        self.fleet = fleet
        self.case_aggregation = FleetCaseAggregation(
            fleet,
            cases,
        )

    @staticmethod
    def _validate_fleet(fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "fleet must be a Fleet."
            )

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

        value = str(value).upper()

        if value not in cls.PRIORITY_WEIGHTS:
            return "UNKNOWN"

        return value

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

    def _fleet_cases(self):
        return self.case_aggregation.cases

    def _occurrences(self):
        occurrences = {}

        for case in self._fleet_cases():
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

        return occurrences

    @classmethod
    def _highest_priority(cls, priority_counts):
        if not priority_counts:
            return "UNKNOWN"

        return max(
            priority_counts,
            key=lambda priority: cls.PRIORITY_WEIGHTS.get(
                priority,
                0,
            ),
        )

    def _score_entry(self, entry):
        priority = self._highest_priority(
            entry["priority_counts"]
        )

        priority_score = self.PRIORITY_WEIGHTS.get(
            priority,
            0,
        )

        machine_count = len(
            entry["machine_ids"]
        )

        fleet_count = self.fleet.machine_count

        if fleet_count > 0:
            machine_impact = (
                machine_count / fleet_count
            )
        else:
            machine_impact = 0.0

        machine_score = round(
            machine_impact * 100,
            4,
        )

        recurrence_score = min(
            entry["occurrence_count"] * 10,
            100,
        )

        fleet_wide = (
            fleet_count > 0
            and machine_count == fleet_count
        )

        fleet_wide_bonus = (
            25
            if fleet_wide
            else 0
        )

        total_score = (
            priority_score
            + machine_score
            + recurrence_score
            + fleet_wide_bonus
        )

        return {
            "priority": priority,
            "priority_score": priority_score,
            "machine_count": machine_count,
            "fleet_machine_count": fleet_count,
            "machine_impact_ratio": machine_impact,
            "machine_impact_score": machine_score,
            "occurrence_count": entry[
                "occurrence_count"
            ],
            "recurrence_score": recurrence_score,
            "fleet_wide": fleet_wide,
            "fleet_wide_bonus": fleet_wide_bonus,
            "total_score": round(
                total_score,
                4,
            ),
        }

    def ranked_recommendations(self):
        ranked = []

        for key, entry in self._occurrences().items():
            score = self._score_entry(entry)

            ranked.append({
                "recommendation_key": key,
                "recommendation": deepcopy(
                    entry["recommendation"]
                ),
                "machine_ids": list(
                    entry["machine_ids"]
                ),
                "case_ids": list(
                    entry["case_ids"]
                ),
                "occurrence_count": (
                    entry["occurrence_count"]
                ),
                "priority_counts": deepcopy(
                    entry["priority_counts"]
                ),
                "scoring": score,
            })

        ranked.sort(
            key=lambda item: (
                -item["scoring"]["total_score"],
                -item["scoring"]["priority_score"],
                item["recommendation_key"],
            )
        )

        for index, item in enumerate(
            ranked,
            start=1,
        ):
            item["rank"] = index

        return deepcopy(ranked)

    def top_recommendation(self):
        ranked = self.ranked_recommendations()

        if not ranked:
            return None

        return ranked[0]

    def affected_machine_ids(self):
        result = []

        for entry in self._occurrences().values():
            for machine_id in entry["machine_ids"]:
                if machine_id not in result:
                    result.append(machine_id)

        return result

    def priority_counts(self):
        counts = {}

        for entry in self._occurrences().values():
            for priority, count in entry[
                "priority_counts"
            ].items():
                counts[priority] = (
                    counts.get(priority, 0)
                    + count
                )

        return counts

    def summary(self):
        ranked = self.ranked_recommendations()

        return {
            "recommendation_count": len(ranked),
            "affected_machine_count": len(
                self.affected_machine_ids()
            ),
            "priority_counts": self.priority_counts(),
            "top_recommendation_key": (
                ranked[0]["recommendation_key"]
                if ranked
                else None
            ),
            "top_score": (
                ranked[0]["scoring"]["total_score"]
                if ranked
                else None
            ),
        }

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "summary": self.summary(),
            "affected_machine_ids": (
                self.affected_machine_ids()
            ),
            "priority_counts": self.priority_counts(),
            "ranked_recommendations": (
                self.ranked_recommendations()
            ),
            "top_recommendation": (
                self.top_recommendation()
            ),
        }
