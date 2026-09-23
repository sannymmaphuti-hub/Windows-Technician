class UserFacingLanguage:
    """Translate diagnostic types into cautious, user-facing language."""

    _TRANSLATIONS = {
        "MEMORY_PRESSURE": (
            "Your computer may be running low on "
            "available memory. This can make Windows "
            "and other programs feel slower."
        ),
        "CPU_PRESSURE": (
            "Your computer's processor may be working "
            "harder than usual. This can make programs "
            "feel slower."
        ),
        "NETWORK_ADAPTER_FAILURE": (
            "Your computer may be having a problem "
            "with its network adapter. This can prevent "
            "it from connecting to the network."
        ),
        "LOCAL_NETWORK_FAILURE": (
            "Your computer may be having trouble "
            "reaching your local network. Check the "
            "network connection and related equipment."
        ),
        "DNS_RESOLUTION_FAILURE": (
            "Your computer may be having trouble "
            "finding the internet address for a website "
            "or online service."
        ),
        "INTERNET_CONNECTIVITY_FAILURE": (
            "Your computer may not be able to reach "
            "the internet right now."
        ),
    }

    _FALLBACK = (
        "The diagnostic system found something "
        "that may need further investigation."
    )

    def translate(self, diagnostic_type):
        """Return cautious language for a diagnostic type."""

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
