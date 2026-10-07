# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC CAPABILITY
# ==========================================


class WindowsDiagnosticCapability:
    """
    Canonical registry of Windows diagnostic capabilities.

    A capability represents a Windows problem domain that the
    current diagnostic architecture recognizes as investigable.

    This class does NOT:
    - perform diagnostics
    - create DiagnosticCase objects
    - create findings
    - authorize remediation
    - execute remediation
    - verify remediation
    - manage workflow
    """

    _SUPPORTED_CAPABILITIES = (
        "PROCESS",
        "MEMORY",
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    )

    @classmethod
    def supported(cls):
        """
        Return the currently supported diagnostic domains.

        A tuple is returned so callers cannot mutate the
        capability registry.
        """
        return cls._SUPPORTED_CAPABILITIES

    @classmethod
    def is_supported(cls, domain):
        """
        Return True when the supplied domain has a diagnostic
        capability.
        """
        if not isinstance(domain, str):
            return False

        normalized = domain.strip().upper()

        return normalized in cls._SUPPORTED_CAPABILITIES

    @classmethod
    def normalize(cls, domain):
        """
        Normalize and validate a diagnostic capability domain.
        """
        if not cls.is_supported(domain):
            raise ValueError(
                f"Unsupported Windows diagnostic capability: "
                f"{domain!r}"
            )

        return domain.strip().upper()