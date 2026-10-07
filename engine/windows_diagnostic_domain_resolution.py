# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC DOMAIN RESOLUTION
# ==========================================


from engine.windows_diagnostic_capability import (
    WindowsDiagnosticCapability,
)

from engine.windows_diagnostic_investigator import (
    WindowsDiagnosticInvestigator,
)

from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)


class WindowsDiagnosticDomainResolution:
    """
    Resolved diagnostic architecture for one Windows problem
    domain.

    This object describes whether a domain is:

    - recognized by the diagnostic architecture
    - assigned an investigator
    - backed by an actual implementation

    This class does NOT:
    - execute diagnostics
    - collect evidence
    - create DiagnosticCase objects
    - create findings
    - authorize remediation
    - execute remediation
    - verify remediation
    - manage technician workflow
    """

    def __init__(
        self,
        domain,
        capability_supported,
        investigator=None,
        engine=None,
    ):
        self.domain = domain
        self.capability_supported = capability_supported
        self.investigator = investigator
        self.engine = engine

        self.implemented = (
            self.capability_supported
            and self.investigator is not None
            and self.engine is not None
        )

    @classmethod
    def resolve(cls, domain):
        """
        Resolve the diagnostic architecture for a Windows
        problem domain.

        Resolution is observational only. It does not execute
        any diagnostic implementation.
        """

        if not isinstance(domain, str):
            return cls(
                domain=None,
                capability_supported=False,
            )

        normalized = domain.strip().upper()

        if not normalized:
            return cls(
                domain=None,
                capability_supported=False,
            )

        capability_supported = (
            WindowsDiagnosticCapability.is_supported(
                normalized
            )
        )

        if not capability_supported:
            return cls(
                domain=normalized,
                capability_supported=False,
            )

        investigator = (
            WindowsDiagnosticInvestigator.for_domain(
                normalized
            )
        )

        registry = WindowsDiagnosticEngineRegistry()

        engine = registry.get_engine(
            normalized
        )

        return cls(
            domain=normalized,
            capability_supported=True,
            investigator=investigator,
            engine=engine,
        )