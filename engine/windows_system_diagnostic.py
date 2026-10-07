from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)
from engine.windows_system_intelligence import (
    WindowsSystemIntelligence,
)


_UNSET = object()


class WindowsSystemDiagnostic:
    domain = "SYSTEM"

    def __init__(self, intelligence=None):
        if intelligence is None:
            intelligence = WindowsSystemIntelligence()

        self.intelligence = intelligence

    def analyze(self, evidence=_UNSET):
        if evidence is _UNSET:
            return self._empty_result()

        if evidence is None:
            raise ValueError(
                "SYSTEM diagnostic requires "
                "WindowsSystemEvidence."
            )

        if not isinstance(
            evidence,
            WindowsSystemEvidence,
        ):
            raise ValueError(
                "SYSTEM diagnostic requires "
                "WindowsSystemEvidence."
            )

        intelligence_result = self.intelligence.analyze(
            evidence
        )

        return WindowsDiagnosticResult(
            observations=[],
            signals=intelligence_result["signals"],
            findings=intelligence_result["findings"],
            correlations=[],
            candidates=[],
            primary_cause=None,
            recommendations=(
                intelligence_result["recommendations"]
            ),
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