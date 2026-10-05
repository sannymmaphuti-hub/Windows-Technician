class TechnicianLanguage:
    """Translate diagnostic types into technician-facing language."""

    _TRANSLATIONS = {
        "MEMORY_PRESSURE": (
            "Memory pressure detected."
        ),
        "CPU_PRESSURE": (
            "CPU pressure detected."
        ),
        "NETWORK_ADAPTER_FAILURE": (
            "Network adapter failure detected."
        ),
        "LOCAL_NETWORK_FAILURE": (
            "Local network connectivity failure detected."
        ),
        "DNS_RESOLUTION_FAILURE": (
            "DNS resolution failure detected."
        ),
        "INTERNET_CONNECTIVITY_FAILURE": (
            "Internet connectivity failure detected."
        ),
    }

    _FALLBACK = "Unknown diagnostic condition."

    def translate(self, diagnostic_type):
        """Return technician-facing language for a diagnostic type."""

        if not isinstance(diagnostic_type, str):
            raise ValueError(
                "diagnostic_type must be a string."
            )

        if not diagnostic_type.strip():
            raise ValueError(
                "diagnostic_type cannot be empty."
            )

        return self._TRANSLATIONS.get(
            diagnostic_type,
            self._FALLBACK,
        )