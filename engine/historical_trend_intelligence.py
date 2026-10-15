from collections import Counter
from copy import deepcopy

from engine.diagnostic_history import DiagnosticHistory


class HistoricalTrendIntelligence:
    """
    Canonical V1.0 historical trend analysis boundary.

    Reads DiagnosticHistory and produces trend intelligence.

    This class does not:
    - mutate historical records
    - mutate DiagnosticCase
    - diagnose live machines
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, history):
        if not isinstance(history, DiagnosticHistory):
            raise ValueError(
                "HistoricalTrendIntelligence requires a DiagnosticHistory."
            )

        self.history = history

    def machine_trend(self, machine_id):
        records = self.history.for_machine(machine_id)

        findings = []
        severities = []

        for record in records:
            for finding in record.findings:
                findings.append(deepcopy(finding))

                if isinstance(finding, dict):
                    severity = finding.get("severity")
                    if severity is not None:
                        severities.append(severity)

        return {
            "machine_id": machine_id,
            "record_count": len(records),
            "finding_count": len(findings),
            "severity_counts": dict(Counter(severities)),
            "findings": findings,
        }

    def recurring_findings(self, machine_id):
        records = self.history.for_machine(machine_id)

        counts = Counter()

        for record in records:
            seen_in_record = set()

            for finding in record.findings:
                if not isinstance(finding, dict):
                    continue

                identity = (
                    finding.get("finding")
                    or finding.get("type")
                    or finding.get("category")
                )

                if identity is not None:
                    seen_in_record.add(identity)

            for identity in seen_in_record:
                counts[identity] += 1

        return [
            {
                "finding": finding,
                "occurrences": occurrences,
            }
            for finding, occurrences in counts.items()
            if occurrences > 1
        ]

    def trend_state(self, machine_id):
        records = self.history.for_machine(machine_id)

        if not records:
            return "NO_HISTORY"

        if len(records) == 1:
            return "INSUFFICIENT_HISTORY"

        finding_counts = []

        for record in records:
            finding_counts.append(len(record.findings))

        if finding_counts[-1] > finding_counts[0]:
            return "WORSENING"

        if finding_counts[-1] < finding_counts[0]:
            return "IMPROVING"

        return "STABLE"

    def projection(self, machine_id):
        return {
            "machine_id": machine_id,
            "trend_state": self.trend_state(machine_id),
            "trend": self.machine_trend(machine_id),
            "recurring_findings": self.recurring_findings(machine_id),
        }
