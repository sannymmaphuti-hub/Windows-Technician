"""Tests for the Windows Technician user guide."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
USER_GUIDE = PROJECT_ROOT / "docs" / "user" / "user_guide.md"


def _guide() -> str:
    return USER_GUIDE.read_text(encoding="utf-8")


def test_user_guide_exists():
    assert USER_GUIDE.is_file()


def test_user_guide_has_core_sections():
    guide = _guide()

    required_sections = (
        "# Windows Technician User Guide",
        "## 1. Starting Windows Technician",
        "## 2. Understanding the Dashboard",
        "## 3. System Health",
        "## 4. Diagnostics",
        "## 5. Findings",
        "## 6. Explanations",
        "## 7. Recommendations",
        "## 8. Remediation",
        "## 9. Authorization and Confirmation",
        "## 10. Remediation Verification",
        "## 12. Recovery",
        "## 14. Privacy and Safety",
        "## 16. Accessibility",
        "## 17. Common Questions",
    )

    for section in required_sections:
        assert section in guide


def test_user_guide_documents_intelligence_flow():
    guide = _guide()

    assert (
        "Observation → Signal → Correlation → Finding → Root Cause "
        "→ Explanation → Recommendation"
    ) in guide


def test_user_guide_documents_remediation_safety_boundary():
    guide = _guide()

    assert (
        "Eligibility → Decision → Authorization → Execution → Verification"
    ) in guide


def test_user_guide_documents_user_safety_boundary():
    guide = _guide()

    assert "Observe → Understand → Decide → Authorize → Act → Verify" in guide


def test_user_guide_distinguishes_diagnosis_from_remediation():
    guide = _guide()

    assert "Recommendations are not automatically executed." in guide
    assert "Remediation authorization is deliberately separate from diagnosis." in guide


def test_user_guide_documents_safe_defaults():
    guide = _guide()

    expected_defaults = (
        "Automatic diagnostics: enabled",
        "Remediation authorization: disabled",
        "Remote operations: disabled",
        "Telemetry: disabled",
        "Logging: enabled",
    )

    for value in expected_defaults:
        assert value in guide


def test_user_guide_warns_against_blind_retry():
    guide = _guide()

    assert "must not blindly retry remediation" in guide
    assert "Do not repeatedly retry blindly." in guide


def test_user_guide_avoids_internal_implementation_details():
    guide = _guide()

    assert "PySide6" not in guide
    assert "PyInstaller" not in guide
    assert "pytest" not in guide
