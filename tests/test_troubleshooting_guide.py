from pathlib import Path


GUIDE = Path("docs/user/troubleshooting.md")


def read_guide() -> str:
    assert GUIDE.exists(), "Troubleshooting guide does not exist."
    return GUIDE.read_text(encoding="utf-8")


def test_troubleshooting_guide_exists():
    assert GUIDE.exists()


def test_troubleshooting_guide_contains_core_sections():
    content = read_guide()

    required_sections = [
        "# Windows Technician Troubleshooting Guide",
        "# 1. Troubleshooting Principle",
        "# 2. Windows Technician Does Not Start",
        "# 6. Recovery After an Interrupted Session",
        "# 9. Recommendation Appears",
        "# 11. Remediation Fails",
        "# 13. Configuration Problems",
        "# 18. Installation Problems",
        "# 19. Upgrade Problems",
        "# 21. Uninstallation Problems",
        "# 23. Packaging Runtime Problems",
        "# 24. When to Stop Troubleshooting",
        "# 26. Troubleshooting Safety Rule",
    ]

    for section in required_sections:
        assert section in content


def test_troubleshooting_guide_contains_safe_sequence():
    content = read_guide()

    assert "Observe → Collect Evidence → Understand → Act → Verify" in content


def test_troubleshooting_guide_rejects_blind_retry():
    content = read_guide()

    assert "Do not blindly repeat a remediation operation." in content
    assert "Do not repeatedly execute the same remediation blindly." in content


def test_troubleshooting_guide_distinguishes_execution_from_verification():
    content = read_guide()

    assert "Executed ≠ Verified" in content


def test_troubleshooting_guide_protects_persistent_data():
    content = read_guide()

    assert "Do not delete the application's persistent data as a first troubleshooting step." in content
    assert "Do not delete persistent data simply because the upgraded application fails." in content


def test_troubleshooting_guide_documents_recovery():
    content = read_guide()

    assert "operational state" in content
    assert "recovery context" in content
    assert "Recovery is not blind retry." in content


def test_troubleshooting_guide_documents_packaged_runtime():
    content = read_guide()

    assert "WindowsTechnician.exe" in content
    assert "_internal" in content
    assert "onedir" in content


def test_troubleshooting_guide_documents_escalation():
    content = read_guide()

    assert "# 24. When to Stop Troubleshooting" in content
    assert "escalate" in content.lower()
    assert "technician" in content.lower()


def test_troubleshooting_guide_is_user_facing():
    content = read_guide()

    forbidden_test_language = [
        "pytest",
        "test_troubleshooting_guide.py",
        "PySide6",
    ]

    for phrase in forbidden_test_language:
        assert phrase not in content
