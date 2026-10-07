"""Tests for the Windows Technician installation lifecycle guide."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUIDE = PROJECT_ROOT / "docs" / "user" / "installation.md"


def _guide() -> str:
    return GUIDE.read_text(encoding="utf-8")


def test_installation_guide_exists():
    assert GUIDE.is_file()


def test_installation_guide_contains_lifecycle_sections():
    guide = _guide()

    required_sections = (
        "# Windows Technician Installation, Upgrade and Uninstall Guide",
        "# 2. Installation",
        "# 3. Application Data",
        "# 4. First Startup",
        "# 6. Upgrading Windows Technician",
        "# 7. Version Direction",
        "# 8. Upgrade Safety",
        "# 10. Uninstallation",
        "# 11. Data Preserved During Normal Uninstallation",
        "# 13. Shortcuts",
        "# 14. Complete Lifecycle",
        "# 18. Safety Principle",
    )

    for section in required_sections:
        assert section in guide


def test_installation_guide_documents_executable():
    guide = _guide()

    assert "WindowsTechnician.exe" in guide
    assert "`_internal`" in guide


def test_installation_guide_documents_verified_lifecycle():
    guide = _guide()

    assert (
        "Build → Package → Validate → Install → Run → Upgrade → Run → Uninstall"
    ) in guide


def test_installation_guide_documents_configuration_preservation():
    guide = _guide()

    assert "Configuration" in guide
    assert "Configuration preservation" in guide


def test_installation_guide_documents_log_and_report_preservation():
    guide = _guide()

    assert "Log preservation" in guide
    assert "Report preservation" in guide


def test_installation_guide_documents_uninstall_boundary():
    guide = _guide()

    assert "Remove Application ≠ Remove User Data" in guide
    assert "Normal uninstallation must not silently delete user data." in guide


def test_installation_guide_documents_upgrade_direction():
    guide = _guide()

    assert "downgrading" in guide
    assert "A lower version must not silently replace a newer installed version" in guide


def test_installation_guide_documents_package_validation_before_replacement():
    guide = _guide()

    assert (
        "validate the replacement package before replacing the existing "
        "application payload"
    ) in guide


def test_installation_guide_keeps_implementation_testing_out():
    guide = _guide()

    assert "pytest" not in guide
    assert "PySide6" not in guide
    assert "test_production_build.py" not in guide
