# ==========================================
# Windows Technician v0.9
# WINDOWS PROBLEM DOMAIN
# ==========================================


class WindowsProblemDomain:
    """
    Canonical registry of Windows problem-solving domains.

    This class identifies areas of Windows that the diagnostic
    architecture can investigate.

    It does NOT perform diagnostics, create cases, authorize
    remediation, or execute operations.
    """

    _SUPPORTED_DOMAINS = (
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
        Return all supported Windows problem domains.

        A tuple prevents callers from modifying the registry.
        """
        return cls._SUPPORTED_DOMAINS

    @classmethod
    def is_supported(cls, domain):
        """
        Return whether a domain is supported.

        Matching is case-insensitive and ignores surrounding
        whitespace.
        """
        if not isinstance(domain, str):
            return False

        normalized = domain.strip().upper()

        return normalized in cls._SUPPORTED_DOMAINS

    @classmethod
    def normalize(cls, domain):
        """
        Normalize a supported domain to its canonical form.
        """
        if not cls.is_supported(domain):
            raise ValueError(
                f"Unsupported Windows problem domain: {domain!r}"
            )

        return domain.strip().upper()