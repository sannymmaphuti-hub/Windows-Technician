from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)


def test_system_evidence_defaults_to_empty_values():
    evidence = WindowsSystemEvidence()

    assert evidence.computer_name == ""
    assert evidence.operating_system == ""
    assert evidence.os_version == ""
    assert evidence.architecture == ""
    assert evidence.processor == ""


def test_system_evidence_stores_system_information():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    assert evidence.computer_name == "TEST-PC"
    assert evidence.operating_system == "Windows"
    assert evidence.os_version == "10.0.26200"
    assert evidence.architecture == "AMD64"
    assert evidence.processor == "AMD Ryzen"


def test_system_evidence_rejects_non_string_values():
    try:
        WindowsSystemEvidence(
            computer_name=123,
        )
    except ValueError:
        return

    raise AssertionError(
        "WindowsSystemEvidence should reject "
        "non-string system information."
    )


def test_system_evidence_preserves_independent_instances():
    first = WindowsSystemEvidence(
        computer_name="FIRST-PC",
        operating_system="Windows",
    )

    second = WindowsSystemEvidence(
        computer_name="SECOND-PC",
        operating_system="Windows",
    )

    assert first.computer_name == "FIRST-PC"
    assert second.computer_name == "SECOND-PC"