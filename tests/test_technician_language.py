from engine.technician_language import TechnicianLanguage


def test_technician_language_can_be_created():
    language = TechnicianLanguage()

    assert language is not None


def test_translates_memory_pressure():
    language = TechnicianLanguage()

    result = language.translate(
        "MEMORY_PRESSURE"
    )

    assert result == "Memory pressure detected."


def test_translates_cpu_pressure():
    language = TechnicianLanguage()

    result = language.translate(
        "CPU_PRESSURE"
    )

    assert result == "CPU pressure detected."


def test_translates_network_adapter_failure():
    language = TechnicianLanguage()

    result = language.translate(
        "NETWORK_ADAPTER_FAILURE"
    )

    assert result == "Network adapter failure detected."


def test_translates_local_network_failure():
    language = TechnicianLanguage()

    result = language.translate(
        "LOCAL_NETWORK_FAILURE"
    )

    assert result == "Local network connectivity failure detected."


def test_translates_dns_resolution_failure():
    language = TechnicianLanguage()

    result = language.translate(
        "DNS_RESOLUTION_FAILURE"
    )

    assert result == "DNS resolution failure detected."


def test_translates_internet_connectivity_failure():
    language = TechnicianLanguage()

    result = language.translate(
        "INTERNET_CONNECTIVITY_FAILURE"
    )

    assert result == "Internet connectivity failure detected."


def test_unknown_diagnostic_type_uses_safe_fallback():
    language = TechnicianLanguage()

    result = language.translate(
        "UNKNOWN_DIAGNOSTIC"
    )

    assert result == "Unknown diagnostic condition."


def test_translation_requires_string():
    language = TechnicianLanguage()

    try:
        language.translate(None)
        assert False
    except ValueError as error:
        assert str(error) == (
            "diagnostic_type must be a string."
        )


def test_translation_rejects_empty_string():
    language = TechnicianLanguage()

    try:
        language.translate("   ")
        assert False
    except ValueError as error:
        assert str(error) == (
            "diagnostic_type cannot be empty."
        )


def test_translation_does_not_modify_input():
    language = TechnicianLanguage()

    diagnostic_type = "MEMORY_PRESSURE"

    language.translate(diagnostic_type)

    assert diagnostic_type == "MEMORY_PRESSURE"


def test_technician_language_does_not_authorize():
    language = TechnicianLanguage()

    assert not hasattr(language, "authorize")


def test_technician_language_does_not_execute():
    language = TechnicianLanguage()

    assert not hasattr(language, "execute")


def test_technician_language_does_not_remediate():
    language = TechnicianLanguage()

    assert not hasattr(language, "remediate")