from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation


class FleetFindingIntelligence:
    """
    Read-only fleet finding intelligence.

    Aggregates findings already produced by canonical DiagnosticCase
    objects belonging to a Fleet.

    This class does not:
    - create findings
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
                "FleetFindingIntelligence requires a Fleet."
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
                    "FleetFindingIntelligence requires DiagnosticCase objects."
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
    def _value(finding, *names):
        if isinstance(finding, dict):
            for name in names:
                value = finding.get(name)
                if value is not None:
                    return value
            return None

        for name in names:
            value = getattr(finding, name, None)
            if value is not None:
                return value

        return None

    @classmethod
    def _finding_key(cls, finding):
        value = cls._value(
            finding,
            "finding_id",
            "finding_type",
            "type",
            "code",
            "name",
            "title",
        )

        if value is not None:
            return str(value)

        if isinstance(finding, dict):
            return str(sorted(finding.items()))

        return str(finding)

    @classmethod
    def _severity(cls, finding):
        value = cls._value(
            finding,
            "severity",
            "priority",
            "level",
        )

        if value is None:
            return "UNKNOWN"

        if hasattr(value, "value"):
            value = value.value

        return str(value).upper()

    def finding_occurrences(self):
        occurrences = {}

        for case in self._fleet_cases():
            for finding in getattr(case, "findings", []):
                key = self._finding_key(finding)

                if key not in occurrences:
                    occurrences[key] = {
                        "finding": deepcopy(finding),
                        "machine_ids": [],
                        "case_ids": [],
                        "occurrence_count": 0,
                        "severity_counts": {},
                    }

                entry = occurrences[key]
                entry["occurrence_count"] += 1

                if case.machine_id not in entry["machine_ids"]:
                    entry["machine_ids"].append(case.machine_id)

                if case.case_id not in entry["case_ids"]:
                    entry["case_ids"].append(case.case_id)

                severity = self._severity(finding)

                entry["severity_counts"][severity] = (
                    entry["severity_counts"].get(severity, 0) + 1
                )

        return deepcopy(occurrences)

    def recurring_findings(self):
        return {
            key: value
            for key, value in self.finding_occurrences().items()
            if len(value["machine_ids"]) > 1
        }

    def affected_machine_ids(self):
        result = []

        for case in self._fleet_cases():
            if getattr(case, "findings", []):
                if case.machine_id not in result:
                    result.append(case.machine_id)

        return result

    def finding_severity_counts(self):
        counts = {}

        for case in self._fleet_cases():
            for finding in getattr(case, "findings", []):
                severity = self._severity(finding)
                counts[severity] = counts.get(severity, 0) + 1

        return counts

    def machine_findings(self):
        result = {}

        for case in self._fleet_cases():
            machine_id = case.machine_id
            result.setdefault(machine_id, [])

            for finding in getattr(case, "findings", []):
                result[machine_id].append({
                    "finding_key": self._finding_key(finding),
                    "severity": self._severity(finding),
                    "case_id": case.case_id,
                })

        return deepcopy(result)

    def summary(self):
        occurrences = self.finding_occurrences()

        return {
            "unique_finding_count": len(occurrences),
            "total_finding_occurrences": sum(
                entry["occurrence_count"]
                for entry in occurrences.values()
            ),
            "recurring_finding_count": len(
                self.recurring_findings()
            ),
            "affected_machine_count": len(
                self.affected_machine_ids()
            ),
            "severity_counts": self.finding_severity_counts(),
        }

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "summary": self.summary(),
            "affected_machine_ids": self.affected_machine_ids(),
            "finding_severity_counts": self.finding_severity_counts(),
            "finding_occurrences": self.finding_occurrences(),
            "recurring_findings": self.recurring_findings(),
            "machine_findings": self.machine_findings(),
        }
