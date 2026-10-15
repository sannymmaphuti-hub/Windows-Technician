from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.historical_evidence import HistoricalEvidence


class DiagnosticHistory:
    """
    Canonical V1.0 historical diagnostic collection boundary.

    Stores HistoricalEvidence snapshots separately from live
    DiagnosticCase lifecycle state.

    This class does not own:
    - DiagnosticCase lifecycle
    - TechnicianWorkflow
    - remediation
    - authorization
    - verification
    """

    def __init__(self):
        self._records = []

    @property
    def records(self):
        return list(self._records)

    @property
    def count(self):
        return len(self._records)

    def record_case(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "DiagnosticHistory requires a DiagnosticCase."
            )

        record = HistoricalEvidence(case)
        self._records.append(record)
        return record

    def add(self, record):
        if not isinstance(record, HistoricalEvidence):
            raise ValueError(
                "DiagnosticHistory requires HistoricalEvidence."
            )

        self._records.append(record)
        return record

    def for_machine(self, machine_id):
        return [
            record
            for record in self._records
            if record.machine_id == machine_id
        ]

    def latest_for_machine(self, machine_id):
        records = self.for_machine(machine_id)
        if not records:
            return None
        return records[-1]

    def projection(self):
        return {
            "count": self.count,
            "records": [
                deepcopy(record.projection())
                for record in self._records
            ],
        }
