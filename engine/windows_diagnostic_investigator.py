# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATOR
# ==========================================

from engine.windows_diagnostic_capability import (
    WindowsDiagnosticCapability,
)


class WindowsDiagnosticInvestigator:
    """
    Canonical investigator boundary for Windows problem domains.

    An investigator identifies the diagnostic responsibility for
    a Windows problem domain.

    This class does NOT:
    - create a DiagnosticCase
    - execute diagnostics during construction
    - own diagnostic results
    - own findings
    - authorize remediation
    - execute remediation
    - verify remediation
    - own technician workflow
    """

    def __init__(self, domain):
        normalized_domain = (
            WindowsDiagnosticCapability.normalize(domain)
        )

        self.domain = normalized_domain

    @classmethod
    def supported(cls):
        """
        Return all domains for which an investigator exists.
        """
        return WindowsDiagnosticCapability.supported()

    @classmethod
    def for_domain(cls, domain):
        """
        Return an investigator for a supported domain.

        Unsupported or invalid domains return None rather than
        creating an invalid investigator.
        """
        if not WindowsDiagnosticCapability.is_supported(
            domain
        ):
            return None

        return cls(domain)