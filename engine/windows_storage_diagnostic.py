# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE DIAGNOSTIC
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)

from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)

from engine.windows_storage_intelligence import (
    WindowsStorageIntelligence,
)


_UNSET = object()


class WindowsStorageDiagnostic:
    """
    Diagnostic implementation for the Windows STORAGE domain.

    The diagnostic accepts optional storage evidence, applies
    the canonical Storage intelligence layer when evidence is
    available, and returns the canonical
    WindowsDiagnosticResult.

    When no evidence argument is supplied, the diagnostic
    preserves the original safe empty-result contract.

    Explicit None evidence is rejected because None does not
    represent valid storage evidence.

    This class does NOT:
    - modify storage
    - delete files
    - repair volumes
    - execute remediation
    - authorize remediation
    - verify remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "STORAGE"

    def __init__(self, intelligence=None):
        if intelligence is None:
            intelligence = WindowsStorageIntelligence()

        self.intelligence = intelligence

    def analyze(self, evidence=_UNSET):
        """
        Analyze Windows storage.

        With evidence:
            Evidence is interpreted by
            WindowsStorageIntelligence.

        Without an evidence argument:
            A safe empty canonical result is returned.

        With explicit None:
            ValueError is raised because None is not valid
            storage evidence.

        No remediation or authorization occurs here.
        """

        if evidence is _UNSET:
            return self._empty_result()

        if evidence is None:
            raise ValueError(
                "Storage diagnostic requires "
                "WindowsStorageEvidence."
            )

        if not isinstance(
            evidence,
            WindowsStorageEvidence,
        ):
            raise ValueError(
                "Storage diagnostic requires "
                "WindowsStorageEvidence."
            )

        intelligence_result = (
            self.intelligence.analyze(evidence)
        )

        return WindowsDiagnosticResult(
            observations=[],
            signals=intelligence_result[
                "signals"
            ],
            findings=intelligence_result[
                "findings"
            ],
            correlations=[],
            candidates=[],
            primary_cause=None,
            recommendations=intelligence_result[
                "recommendations"
            ],
            confidences=[],
        )

    @staticmethod
    def _empty_result():
        return WindowsDiagnosticResult(
            observations=[],
            signals=[],
            findings=[],
            correlations=[],
            candidates=[],
            primary_cause=None,
            recommendations=[],
            confidences=[],
        )