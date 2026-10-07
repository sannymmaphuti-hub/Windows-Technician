# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC RESULT NORMALIZER
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)


class WindowsDiagnosticResultNormalizer:
    """
    Normalizes diagnostic output into the canonical
    WindowsDiagnosticResult boundary.

    Supported source formats:

        WindowsDiagnosticResult
        dictionary

    A canonical WindowsDiagnosticResult is returned in
    every successful case.

    This class does NOT:
    - execute diagnostics
    - create DiagnosticCase objects
    - manage case lifecycle
    - authorize remediation
    - execute remediation
    - verify remediation
    - manage technician workflow
    """

    @classmethod
    def normalize(cls, result):
        """
        Convert supported diagnostic output into a
        WindowsDiagnosticResult.

        Existing canonical results are returned unchanged.
        Legacy dictionaries are converted into a new
        canonical result.
        """

        if isinstance(
            result,
            WindowsDiagnosticResult,
        ):
            return result

        if isinstance(result, dict):
            return cls._from_dictionary(result)

        if result is None:
            raise ValueError(
                "diagnostic result cannot be None."
            )

        raise ValueError(
            "unsupported diagnostic result type."
        )

    @staticmethod
    def _from_dictionary(result):
        """
        Convert a legacy dictionary result into the
        canonical WindowsDiagnosticResult.
        """

        return WindowsDiagnosticResult(
            observations=result.get(
                "observations",
                [],
            ),
            signals=result.get(
                "signals",
                [],
            ),
            findings=result.get(
                "findings",
                [],
            ),
            correlations=result.get(
                "correlations",
                [],
            ),
            candidates=result.get(
                "candidates",
                [],
            ),
            primary_cause=result.get(
                "primary_cause",
                None,
            ),
            recommendations=result.get(
                "recommendations",
                [],
            ),
            confidences=result.get(
                "confidences",
                [],
            ),
        )