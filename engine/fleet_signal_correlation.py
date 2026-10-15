from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetSignalCorrelation:
    """
    Read-only cross-machine signal correlation.

    Correlates signals already present on canonical DiagnosticCase
    objects belonging to a Fleet.

    This class does not:
    - create signals
    - mutate DiagnosticCase objects
    - diagnose machines
    - infer root causes
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, fleet, cases=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetSignalCorrelation requires a Fleet."
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
                    "FleetSignalCorrelation requires DiagnosticCase objects."
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
    def _signal_key(signal):
        if isinstance(signal, dict):
            for key in (
                "signal_id",
                "name",
                "signal_type",
                "type",
                "code",
            ):
                if key in signal:
                    value = signal[key]
                    if value is not None:
                        return str(value)

            return str(sorted(signal.items()))

        for attribute in (
            "signal_id",
            "name",
            "signal_type",
            "type",
            "code",
        ):
            value = getattr(signal, attribute, None)
            if value is not None:
                return str(value)

        return str(signal)

    def signal_occurrences(self):
        occurrences = {}

        for case in self._fleet_cases():
            for signal in getattr(case, "signals", []):
                key = self._signal_key(signal)

                occurrences.setdefault(
                    key,
                    {
                        "signal": deepcopy(signal),
                        "machine_ids": [],
                        "case_ids": [],
                        "occurrence_count": 0,
                    },
                )

                entry = occurrences[key]
                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(case.machine_id)

                if case.case_id not in entry["case_ids"]:
                    entry["case_ids"].append(case.case_id)

        return deepcopy(occurrences)

    def recurring_signals(self):
        return {
            key: value
            for key, value in self.signal_occurrences().items()
            if len(value["machine_ids"]) > 1
        }

    def fleet_wide_signals(self):
        machine_count = self.fleet.machine_count

        return {
            key: value
            for key, value in self.signal_occurrences().items()
            if len(value["machine_ids"]) == machine_count
            and machine_count > 0
        }

    def affected_machine_ids(self):
        result = []

        for case in self._fleet_cases():
            if getattr(case, "signals", []):
                if case.machine_id not in result:
                    result.append(case.machine_id)

        return result

    def machine_signal_counts(self):
        result = {}

        for case in self._fleet_cases():
            machine_id = case.machine_id
            result.setdefault(machine_id, 0)
            result[machine_id] += len(
                getattr(case, "signals", [])
            )

        return deepcopy(result)

    def correlation_summary(self):
        occurrences = self.signal_occurrences()

        return {
            "unique_signal_count": len(occurrences),
            "recurring_signal_count": len(
                self.recurring_signals()
            ),
            "fleet_wide_signal_count": len(
                self.fleet_wide_signals()
            ),
            "affected_machine_count": len(
                self.affected_machine_ids()
            ),
            "total_signal_occurrences": sum(
                entry["occurrence_count"]
                for entry in occurrences.values()
            ),
        }

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "summary": self.correlation_summary(),
            "affected_machine_ids": self.affected_machine_ids(),
            "machine_signal_counts": self.machine_signal_counts(),
            "signal_occurrences": self.signal_occurrences(),
            "recurring_signals": self.recurring_signals(),
            "fleet_wide_signals": self.fleet_wide_signals(),
        }
