# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATION COORDINATOR
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)


class WindowsDiagnosticInvestigationCoordinator:
    _RESULT_FIELDS = {
        "observations": "set_observations",
        "signals": "set_signals",
        "findings": "set_findings",
        "correlations": "set_correlations",
        "candidates": "set_root_cause_candidates",
        "primary_cause": "set_primary_root_cause",
    }

    def attach_result(self, case, result):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "attach_result requires a DiagnosticCase."
            )

        if result is None:
            raise ValueError(
                "attach_result requires a diagnostic result."
            )

        if isinstance(
            result,
            WindowsDiagnosticResult,
        ):
            return self._attach_canonical_result(
                case,
                result,
            )

        if isinstance(result, dict):
            return self._attach_dictionary_result(
                case,
                result,
            )

        raise ValueError(
            "diagnostic result must be a "
            "WindowsDiagnosticResult or dictionary."
        )

    def _attach_canonical_result(
        self,
        case,
        result,
    ):
        # Preserve the canonical object graph.
        #
        # Signals referenced by findings must remain
        # the exact same objects as the signals attached
        # to the case.
        case.observations = result.observations
        case.signals = result.signals
        case.findings = result.findings
        case.correlations = result.correlations
        case.root_cause_candidates = result.candidates
        case.primary_root_cause = result.primary_cause
        case.recommendations = result.recommendations

        return case

    def _attach_dictionary_result(
        self,
        case,
        result,
    ):
        for field, setter_name in (
            self._RESULT_FIELDS.items()
        ):
            value = result.get(
                field,
                None
                if field == "primary_cause"
                else [],
            )

            getattr(
                case,
                setter_name,
            )(value)

        return case