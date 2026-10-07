# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATION ORCHESTRATOR
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)
from engine.windows_diagnostic_investigation_coordinator import (
    WindowsDiagnosticInvestigationCoordinator,
)
from engine.windows_diagnostic_result_normalizer import (
    WindowsDiagnosticResultNormalizer,
)


_UNSET = object()


class WindowsDiagnosticInvestigationOrchestrator:
    def __init__(self):
        self.dispatcher = (
            WindowsDiagnosticDispatcher()
        )

        self.normalizer = (
            WindowsDiagnosticResultNormalizer()
        )

        self.coordinator = (
            WindowsDiagnosticInvestigationCoordinator()
        )

    def investigate(
        self,
        case,
        domain,
        evidence=_UNSET,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "investigate requires a DiagnosticCase."
            )

        if domain is None:
            raise ValueError(
                "investigate requires a diagnostic domain."
            )

        if evidence is _UNSET:
            if domain in {"PROCESS", "MEMORY"}:
                diagnostic_result = (
                    self.dispatcher.dispatch(
                        domain,
                        evidence=None,
                    )
                )
            else:
                diagnostic_result = (
                    self.dispatcher.dispatch(
                        domain,
                    )
                )
        else:
            diagnostic_result = (
                self.dispatcher.dispatch(
                    domain,
                    evidence=evidence,
                )
            )

        canonical_result = (
            self.normalizer.normalize(
                diagnostic_result
            )
        )

        self.coordinator.attach_result(
            case,
            canonical_result,
        )

        return case