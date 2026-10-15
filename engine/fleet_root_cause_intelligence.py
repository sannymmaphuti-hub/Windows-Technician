from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetRootCauseIntelligence:
    """
    Read-only fleet root-cause intelligence.

    Aggregates root-cause evidence already produced by canonical
    DiagnosticCase objects belonging to a Fleet.

    This class does not:
    - infer new root causes
    - run root-cause analysis
    - mutate DiagnosticCase objects
    - create findings
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, fleet, cases=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetRootCauseIntelligence requires a Fleet."
            )

        if cases is None:
            cases = []

        if not isinstance(cases, (list, tuple)):
            raise ValueError(
                "cases must be a list or tuple."
            )

        for case in cases:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "FleetRootCauseIntelligence requires DiagnosticCase objects."
                )

        self.fleet = fleet
        self.case_aggregation = FleetCaseAggregation(
            fleet,
            cases,
        )

    def _fleet_cases(self):
        fleet_machine_ids = set(self.fleet.machine_ids)

        return [
            case
            for case in self.case_aggregation.cases
            if case.machine_id in fleet_machine_ids
        ]

    @staticmethod
    def _value(root_cause, *names):
        if isinstance(root_cause, dict):
            for name in names:
                value = root_cause.get(name)
                if value is not None:
                    return value
            return None

        for name in names:
            value = getattr(root_cause, name, None)
            if value is not None:
                return value

        return None

    @classmethod
    def _cause_key(cls, root_cause):
        value = cls._value(
            root_cause,
            "cause_id",
            "root_cause_id",
            "cause_type",
            "category",
            "name",
            "type",
        )

        if value is not None:
            if hasattr(value, "value"):
                value = value.value
            return str(value)

        if isinstance(root_cause, dict):
            return str(sorted(root_cause.items()))

        return str(root_cause)

    @classmethod
    def _confidence(cls, root_cause):
        value = cls._value(
            root_cause,
            "confidence",
            "confidence_score",
            "score",
        )

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def root_cause_occurrences(self):
        occurrences = {}

        for case in self._fleet_cases():
            root_causes = getattr(
                case,
                "root_causes",
                [],
            )

            for root_cause in root_causes:
                key = self._cause_key(root_cause)

                if key not in occurrences:
                    occurrences[key] = {
                        "root_cause": deepcopy(root_cause),
                        "machine_ids": [],
                        "case_ids": [],
                        "occurrence_count": 0,
                        "confidence_values": [],
                    }

                entry = occurrences[key]
                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(case.machine_id)

                if case.case_id not in entry["case_ids"]:
                    entry["case_ids"].append(case.case_id)

                confidence = self._confidence(root_cause)

                if confidence is not None:
                    entry["confidence_values"].append(
                        confidence
                    )

        return deepcopy(occurrences)

    def recurring_root_causes(self):
        return {
            key: value
            for key, value in self.root_cause_occurrences().items()
            if len(value["machine_ids"]) > 1
        }

    def affected_machine_ids(self):
        result = []

        for case in self._fleet_cases():
            if getattr(case, "root_causes", []):
                if case.machine_id not in result:
                    result.append(case.machine_id)

        return result

    def machine_root_causes(self):
        result = {}

        for case in self._fleet_cases():
            machine_id = case.machine_id
            result.setdefault(machine_id, [])

            for root_cause in getattr(
                case,
                "root_causes",
                [],
            ):
                result[machine_id].append({
                    "root_cause_key": self._cause_key(
                        root_cause
                    ),
                    "case_id": case.case_id,
                    "confidence": self._confidence(
                        root_cause
                    ),
                })

        return deepcopy(result)

    def summary(self):
        occurrences = self.root_cause_occurrences()

        return {
            "unique_root_cause_count": len(
                occurrences
            ),
            "total_root_cause_occurrences": sum(
                entry["occurrence_count"]
                for entry in occurrences.values()
            ),
            "recurring_root_cause_count": len(
                self.recurring_root_causes()
            ),
            "affected_machine_count": len(
                self.affected_machine_ids()
            ),
        }

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "summary": self.summary(),
            "affected_machine_ids": self.affected_machine_ids(),
            "root_cause_occurrences": (
                self.root_cause_occurrences()
            ),
            "recurring_root_causes": (
                self.recurring_root_causes()
            ),
            "machine_root_causes": (
                self.machine_root_causes()
            ),
        }
