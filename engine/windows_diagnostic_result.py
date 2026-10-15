# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC RESULT
# ==========================================

from copy import deepcopy


class WindowsDiagnosticResult:
    """
    Canonical result container for Windows diagnostics.

    The result owns its collection containers but preserves
    relationships between canonical diagnostic objects such as
    Signal, Finding, and Recommendation.

    This class does NOT:
    - authorize remediation
    - execute remediation
    - verify remediation
    - manage technician workflow
    - create recovery operations
    """

    def __init__(
        self,
        observations=None,
        signals=None,
        findings=None,
        correlations=None,
        candidates=None,
        primary_cause=None,
        recommendations=None,
        confidences=None,
    ):
        self.observations = list(
            observations
            if observations is not None
            else []
        )

        self.signals = list(
            signals
            if signals is not None
            else []
        )

        raw_findings = (
            findings
            if findings is not None
            else []
        )

        self.findings = [
            deepcopy(finding)
            if isinstance(
                finding,
                (dict, list, tuple, set),
            )
            else finding
            for finding in raw_findings
        ]

        self.correlations = list(
            correlations
            if correlations is not None
            else []
        )

        self.candidates = list(
            candidates
            if candidates is not None
            else []
        )

        self.primary_cause = deepcopy(
            primary_cause
        )

        self.recommendations = list(
            recommendations
            if recommendations is not None
            else []
        )

        self.confidences = list(
            confidences
            if confidences is not None
            else []
        )

    def __getitem__(self, key):
        """Provide dictionary-style read access for legacy callers."""
        if key not in {
            "observations",
            "signals",
            "findings",
            "correlations",
            "candidates",
            "primary_cause",
            "recommendations",
            "confidences",
        }:
            raise KeyError(key)

        return getattr(self, key)

    def get(self, key, default=None):
        """Provide dictionary-style get() compatibility."""
        try:
            return self[key]
        except KeyError:
            return default
