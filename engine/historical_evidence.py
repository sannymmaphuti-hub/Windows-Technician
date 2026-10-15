from copy import deepcopy
from datetime import datetime, timezone

from engine.diagnostic_case import DiagnosticCase


class HistoricalEvidence:
    """
    Canonical V1.0 historical evidence record.

    Captures an immutable-style snapshot of evidence from a
    DiagnosticCase.

    This class does not own:
    - DiagnosticCase lifecycle
    - TechnicianWorkflow
    - remediation
    - authorization
    - verification
    - recommendations
    """

    def __init__(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "HistoricalEvidence requires a DiagnosticCase."
            )

        self._machine_id = getattr(case, "machine_id", None)
        self._hostname = getattr(case, "hostname", None)
        self._timestamp = datetime.now(timezone.utc).isoformat()

        self._observations = deepcopy(case.observations)
        self._signals = deepcopy(case.signals)
        self._correlations = deepcopy(case.correlations)
        self._findings = deepcopy(case.findings)

    @property
    def machine_id(self):
        return self._machine_id

    @property
    def hostname(self):
        return self._hostname

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def observations(self):
        return deepcopy(self._observations)

    @property
    def signals(self):
        return deepcopy(self._signals)

    @property
    def correlations(self):
        return deepcopy(self._correlations)

    @property
    def findings(self):
        return deepcopy(self._findings)

    def projection(self):
        return {
            "machine_id": self.machine_id,
            "hostname": self.hostname,
            "timestamp": self.timestamp,
            "observations": self.observations,
            "signals": self.signals,
            "correlations": self.correlations,
            "findings": self.findings,
        }
