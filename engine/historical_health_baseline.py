from copy import deepcopy

from engine.diagnostic_history import DiagnosticHistory


class HistoricalHealthBaseline:
    """
    Canonical V1.0 historical health baseline boundary.

    Builds a machine-specific baseline from historical diagnostic
    evidence.

    This class does not:
    - mutate DiagnosticCase
    - mutate DiagnosticHistory
    - diagnose live systems
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, history):
        if not isinstance(history, DiagnosticHistory):
            raise ValueError(
                "HistoricalHealthBaseline requires a DiagnosticHistory."
            )

        self.history = history

    def machine_baseline(self, machine_id):
        records = self.history.for_machine(machine_id)

        finding_counts = {}
        severity_counts = {}

        for record in records:
            seen_findings = set()
            seen_severities = set()

            for finding in record.findings:
                if not isinstance(finding, dict):
                    continue

                identity = (
                    finding.get("finding")
                    or finding.get("type")
                    or finding.get("category")
                )

                if identity is not None:
                    seen_findings.add(identity)

                severity = finding.get("severity")

                if severity is not None:
                    seen_severities.add(severity)

            for finding in seen_findings:
                finding_counts[finding] = (
                    finding_counts.get(finding, 0) + 1
                )

            for severity in seen_severities:
                severity_counts[severity] = (
                    severity_counts.get(severity, 0) + 1
                )

        record_count = len(records)

        recurring_findings = {
            finding: count
            for finding, count in finding_counts.items()
            if count > 1
        }

        return {
            "machine_id": machine_id,
            "record_count": record_count,
            "finding_counts": deepcopy(finding_counts),
            "severity_counts": deepcopy(severity_counts),
            "recurring_findings": deepcopy(recurring_findings),
        }

    def known_problems(self, machine_id):
        baseline = self.machine_baseline(machine_id)
        return list(baseline["finding_counts"].keys())

    def common_problems(self, machine_id, minimum_occurrences=2):
        if not isinstance(minimum_occurrences, int):
            raise ValueError(
                "minimum_occurrences must be an integer."
            )

        if minimum_occurrences < 1:
            raise ValueError(
                "minimum_occurrences must be at least 1."
            )

        baseline = self.machine_baseline(machine_id)

        return {
            finding: count
            for finding, count in baseline["finding_counts"].items()
            if count >= minimum_occurrences
        }

    def has_baseline(self, machine_id):
        return self.machine_baseline(machine_id)["record_count"] > 0

    def projection(self, machine_id):
        baseline = self.machine_baseline(machine_id)

        return {
            "machine_id": machine_id,
            "has_baseline": baseline["record_count"] > 0,
            "baseline": deepcopy(baseline),
            "known_problems": self.known_problems(machine_id),
        }
