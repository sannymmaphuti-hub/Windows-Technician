# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES DIAGNOSTIC
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)

from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)

from engine.windows_services_intelligence import (
    WindowsServicesIntelligence,
)


_UNSET = object()


class WindowsServicesDiagnostic:
    """
    Diagnostic implementation for the Windows SERVICES domain.

    No evidence argument preserves the safe empty-result
    compatibility contract.

    Explicit None is rejected.

    This class does NOT:
    - modify services
    - start services
    - stop services
    - enable services
    - disable services
    - authorize remediation
    - execute remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "SERVICES"

    def __init__(self, intelligence=None):
        if intelligence is None:
            intelligence = WindowsServicesIntelligence()

        self.intelligence = intelligence

    def analyze(self, evidence=_UNSET):
        if evidence is _UNSET:
            return self._empty_result()

        if evidence is None:
            raise ValueError(
                "Services diagnostic requires "
                "WindowsServicesEvidence."
            )

        if not isinstance(
            evidence,
            WindowsServicesEvidence,
        ):
            raise ValueError(
                "Services diagnostic requires "
                "WindowsServicesEvidence."
            )

        intelligence_result = (
            self.intelligence.analyze(evidence)
        )

        return WindowsDiagnosticResult(
            observations=[],
            signals=intelligence_result["signals"],
            findings=intelligence_result["findings"],
            correlations=[],
            candidates=[],
            primary_cause=None,
            recommendations=(
                intelligence_result[
                    "recommendations"
                ]
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