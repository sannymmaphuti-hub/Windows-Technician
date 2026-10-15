from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetAnomalyIntelligence:
    """
    Canonical V1.0 fleet anomaly intelligence.

    Detects deterministic, explainable deviations in signals,
    findings, recommendations, and machine activity across a Fleet.

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
    def _signal_key(signal):
        if isinstance(signal, dict):
            for name in (
                "signal_id",
                "name",
                "signal_type",
                "type",
                "code",
            ):
                value = signal.get(name)

                if value is not None:
                    return str(value)

            return str(sorted(signal.items()))

        for name in (
            "signal_id",
            "name",
            "signal_type",
            "type",
            "code",
        ):
            value = getattr(
                signal,
                name,
                None,
            )

            if value is not None:
                return str(value)

        return str(signal)

    @staticmethod
    def _finding_key(finding):
        if isinstance(finding, dict):
            for name in (
                "finding_id",
                "finding_type",
                "type",
                "code",
                "name",
                "title",
            ):
                value = finding.get(name)

                if value is not None:
                    return str(value)

            return str(sorted(finding.items()))

        for name in (
            "finding_id",
            "finding_type",
            "type",
            "code",
            "name",
            "title",
        ):
            value = getattr(
                finding,
                name,
                None,
            )

            if value is not None:
                return str(value)

        return str(finding)

    @staticmethod
    def _recommendation_key(recommendation):
        if isinstance(recommendation, dict):
            for name in (
                "recommendation_id",
                "recommendation_type",
                "type",
                "code",
                "name",
                "category",
                "description",
            ):
                value = recommendation.get(name)

                if value is not None:
                    return str(value)

            return str(sorted(recommendation.items()))

        for name in (
            "recommendation_id",
            "recommendation_type",
            "type",
            "code",
            "name",
            "category",
            "description",
        ):
            value = getattr(
                recommendation,
                name,
                None,
            )

            if value is not None:
                return str(value)

        return str(recommendation)

    def _fleet_cases(self):
        return self.case_aggregation.cases

    def machine_activity(self):
        """
        Return per-machine intelligence activity counts.
        """
        result = {}

        for machine in self.fleet.machines:
            result[machine.machine_id] = {
                "case_count": 0,
                "signal_count": 0,
                "finding_count": 0,
                "recommendation_count": 0,
            }

        for case in self._fleet_cases():
            machine_id = case.machine_id

            if machine_id not in result:
                result[machine_id] = {
                    "case_count": 0,
                    "signal_count": 0,
                    "finding_count": 0,
                    "recommendation_count": 0,
                }

            result[machine_id]["case_count"] += 1
            result[machine_id]["signal_count"] += len(
                getattr(case, "signals", [])
            )
            result[machine_id]["finding_count"] += len(
                getattr(case, "findings", [])
            )
            result[machine_id]["recommendation_count"] += len(
                getattr(case, "recommendations", [])
            )

        return deepcopy(result)

    def signal_distribution(self):
        distribution = {}

        for case in self._fleet_cases():
            for signal in getattr(case, "signals", []):
                key = self._signal_key(signal)

                entry = distribution.setdefault(
                    key,
                    {
                        "signal": deepcopy(signal),
                        "machine_ids": [],
                        "occurrence_count": 0,
                    },
                )

                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(
                        case.machine_id
                    )

        return deepcopy(distribution)

    def finding_distribution(self):
        distribution = {}

        for case in self._fleet_cases():
            for finding in getattr(case, "findings", []):
                key = self._finding_key(finding)

                entry = distribution.setdefault(
                    key,
                    {
                        "finding": deepcopy(finding),
                        "machine_ids": [],
                        "occurrence_count": 0,
                    },
                )

                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(
                        case.machine_id
                    )

        return deepcopy(distribution)

    def recommendation_distribution(self):
        distribution = {}

        for case in self._fleet_cases():
            for recommendation in getattr(
                case,
                "recommendations",
                [],
            ):
                key = self._recommendation_key(
                    recommendation
                )

                entry = distribution.setdefault(
                    key,
                    {
                        "recommendation": deepcopy(
                            recommendation
                        ),
                        "machine_ids": [],
                        "occurrence_count": 0,
                    },
                )

                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(
                        case.machine_id
                    )

        return deepcopy(distribution)

    def _outliers_from_distribution(
        self,
        distribution,
        minimum_machine_ratio=0.5,
    ):
        machine_count = self.fleet.machine_count

        if machine_count == 0:
            return {}

        result = {}

        for key, entry in distribution.items():
            affected_count = len(
                entry["machine_ids"]
            )

            ratio = (
                affected_count / machine_count
            )

            if ratio < minimum_machine_ratio:
                result[key] = {
                    **deepcopy(entry),
                    "affected_machine_count": affected_count,
                    "machine_ratio": ratio,
                }

        return deepcopy(result)

    def signal_outliers(self):
        return self._outliers_from_distribution(
            self.signal_distribution()
        )

    def finding_outliers(self):
        return self._outliers_from_distribution(
            self.finding_distribution()
        )

    def recommendation_outliers(self):
        return self._outliers_from_distribution(
            self.recommendation_distribution()
        )

    def machine_outliers(self):
        """
        Identify machines whose case activity is unusually
        concentrated within the fleet.

        The baseline uses active machines so inactive machines do
        not artificially lower the average.

        A machine is considered an outlier when:
        - its case activity is strictly above the active-machine
          average, or
        - it is the sole active machine while other fleet machines
          have no cases.

        This keeps equal activity across active machines normal while
        still detecting extreme fleet-wide concentration.
        """
        activity = self.machine_activity()

        if not activity:
            return {}

        active_case_counts = [
            values["case_count"]
            for values in activity.values()
            if values["case_count"] > 0
        ]

        if not active_case_counts:
            return {}

        average = (
            sum(active_case_counts)
            / len(active_case_counts)
        )

        active_machine_count = len(active_case_counts)
        fleet_machine_count = len(activity)

        result = {}

        for machine_id, values in activity.items():
            case_count = values["case_count"]

            if case_count <= 0:
                continue

            above_average = case_count > average

            sole_active_machine = (
                active_machine_count == 1
                and fleet_machine_count > 1
            )

            if above_average or sole_active_machine:
                result[machine_id] = {
                    **deepcopy(values),
                    "fleet_average_case_count": average,
                    "deviation": case_count - average,
                }

        return deepcopy(result)

    def anomaly_summary(self):
        return {
            "signal_outlier_count": len(
                self.signal_outliers()
            ),
            "finding_outlier_count": len(
                self.finding_outliers()
            ),
            "recommendation_outlier_count": len(
                self.recommendation_outliers()
            ),
            "machine_outlier_count": len(
                self.machine_outliers()
            ),
        }

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "summary": self.anomaly_summary(),
            "machine_activity": self.machine_activity(),
            "signal_distribution": self.signal_distribution(),
            "finding_distribution": self.finding_distribution(),
            "recommendation_distribution": (
                self.recommendation_distribution()
            ),
            "signal_outliers": self.signal_outliers(),
            "finding_outliers": self.finding_outliers(),
            "recommendation_outliers": (
                self.recommendation_outliers()
            ),
            "machine_outliers": self.machine_outliers(),
        }
