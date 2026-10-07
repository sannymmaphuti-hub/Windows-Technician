# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP DIAGNOSTIC
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)
from engine.windows_startup_intelligence import (
    WindowsStartupIntelligence,
)


_UNSET = object()


class WindowsStartupDiagnostic:
    domain = "STARTUP"

    def __init__(self, intelligence=None):
        if intelligence is None:
            intelligence = WindowsStartupIntelligence()

        self.intelligence = intelligence

    def analyze(self, evidence=_UNSET):
        if evidence is _UNSET:
            return self._empty_result()

        if evidence is None:
            raise ValueError(
                "Startup diagnostic requires "
                "WindowsStartupEvidence."
            )

        if not isinstance(
            evidence,
            WindowsStartupEvidence,
        ):
            raise ValueError(
                "Startup diagnostic requires "
                "WindowsStartupEvidence."
            )

        intelligence_result = (
            self.intelligence.analyze(
                evidence
            )
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