from engine.user_facing_language import UserFacingLanguage


def test_translates_memory_pressure():
    language = UserFacingLanguage()

    result = language.translate(
        "MEMORY_PRESSURE"
    )

    assert result == (
        "Your computer may be running low on "
        "available memory. This can make Windows "
        "and other programs feel slower."
    )


def test_translates_cpu_pressure():
    language = UserFacingLanguage()

    result = language.translate(
        "CPU_PRESSURE"
    )

    assert result == (
        "Your computer's processor may be working "
        "harder than usual. This can make programs "
        "feel slower."
    )


def test_translates_network_adapter_failure():
    language = UserFacingLanguage()

    result = language.translate(
        "NETWORK_ADAPTER_FAILURE"
    )

    assert result == (
        "Your computer may be having a problem "
        "with its network adapter. This can prevent "
        "it from connecting to the network."
    )


def test_translates_local_network_failure():
    language = UserFacingLanguage()

    result = language.translate(
        "LOCAL_NETWORK_FAILURE"
    )

    assert result == (
        "Your computer may be having trouble "
        "reaching your local network. Check the "
        "network connection and related equipment."
    )


def test_translates_dns_resolution_failure():
    language = UserFacingLanguage()

    result = language.translate(
        "DNS_RESOLUTION_FAILURE"
    )

    assert result == (
        "Your computer may be having trouble "
        "finding the internet address for a website "
        "or online service."
    )


def test_translates_internet_connectivity_failure():
    language = UserFacingLanguage()

    result = language.translate(
        "INTERNET_CONNECTIVITY_FAILURE"
    )

    assert result == (
        "Your computer may not be able to reach "
        "the internet right now."
    )


def test_unknown_diagnostic_type_uses_safe_fallback():
    language = UserFacingLanguage()

    result = language.translate(
        "UNKNOWN_DIAGNOSTIC"
    )

    assert result == (
        "The diagnostic system found something "
        "that may need further investigation."
    )


def test_translation_does_not_claim_certainty():
    language = UserFacingLanguage()

    result = language.translate(
        "MEMORY_PRESSURE"
    )

    assert "is definitely" not in result
    assert "confirmed" not in result
    assert "caused by" not in result


def test_translation_does_not_modify_input():
    language = UserFacingLanguage()

    diagnostic_type = "MEMORY_PRESSURE"

    language.translate(diagnostic_type)

    assert diagnostic_type == "MEMORY_PRESSURE"


def test_translation_requires_string():
    language = UserFacingLanguage()

    try:
        language.translate(None)
        assert False
    except ValueError as error:
        assert str(error) == (
            "diagnostic_type must be a string."
        )


def test_translation_rejects_empty_string():
    language = UserFacingLanguage()

    try:
        language.translate("   ")
        assert False
    except ValueError as error:
        assert str(error) == (
            "diagnostic_type cannot be empty."
        )