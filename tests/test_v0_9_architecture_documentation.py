"""Tests for the canonical Windows Technician v0.9 architecture document."""

from pathlib import Path


ARCHITECTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "architecture"
    / "v0.9_architecture.md"
)


def read_architecture() -> str:
    assert ARCHITECTURE_PATH.is_file()
    return ARCHITECTURE_PATH.read_text(encoding="utf-8-sig")


def test_architecture_document_exists():
    assert ARCHITECTURE_PATH.is_file()


def test_v09_identity():
    text = read_architecture()
    assert "# Windows Technician v0.9 Architecture" in text


def test_canonical_diagnostic_chain():
    text = read_architecture()
    assert (
        "Observation → Signal → Correlation → Finding → Root Cause "
        "→ Explanation → Recommendation → Diagnostic Case"
    ) in text


def test_canonical_remediation_chain():
    text = read_architecture()
    assert (
        "Eligibility → Decision → Authorization → Execution → Verification"
    ) in text


def test_diagnostic_case_is_canonical():
    text = read_architecture()
    assert "DiagnosticCase" in text
    assert "canonical diagnostic case model" in text


def test_technician_workflow_is_canonical():
    text = read_architecture()
    assert "TechnicianWorkflow" in text
    assert "canonical workflow boundary" in text


def test_execution_and_verification_are_distinct():
    text = read_architecture()
    assert "Executed ≠ Verified" in text
    assert "Execution does not imply verification." in text


def test_recovery_does_not_blind_retry():
    text = read_architecture()
    assert "Recovery must not become automatic blind retry." in text
    assert "blind retry" in text.lower()


def test_remote_architecture_is_canonical():
    text = read_architecture()
    assert "RemoteSession" in text
    assert "RemoteMachine" in text
    assert (
        "Technician → RemoteSession → RemoteMachine → Diagnostic → "
        "Case → Decision → Remediation → Verification"
    ) in text


def test_machine_and_case_identity_are_distinct():
    text = read_architecture()
    assert "Machine identity and case identity remain distinct." in text


def test_application_runtime_is_canonical():
    text = read_architecture()
    assert "ApplicationRuntime" in text
    assert "CREATED → STARTING → RUNNING → DEGRADED/FAILED → STOPPING → STOPPED" in text


def test_production_services_are_defined():
    text = read_architecture()
    for service in (
        "Configuration",
        "Diagnostics",
        "Intelligence",
        "Logging",
        "UI",
    ):
        assert service in text


def test_runtime_paths_are_documented():
    text = read_architecture()
    assert "%LOCALAPPDATA%\\WindowsTechnician\\" in text


def test_operational_state_and_recovery_are_documented():
    text = read_architecture()
    assert "Operational State" in text
    assert "Startup Recovery" in text
    assert "recovery state" in text


def test_system_wide_intelligence_is_documented():
    text = read_architecture()
    assert "System-Wide Intelligence" in text
    assert "system-wide intelligence" in text.lower()


def test_historical_intelligence_is_documented():
    text = read_architecture()
    assert "Historical Intelligence" in text
    assert "previous observations" in text


def test_fleet_architecture_is_documented():
    text = read_architecture()
    assert "Fleet and Multi-Machine Architecture" in text
    assert "Fleet Intelligence" in text
    assert "fleet identity" in text


def test_proactive_operations_use_canonical_case_model():
    text = read_architecture()
    assert "Proactive Operations" in text
    assert "existing DiagnosticCase and TechnicianWorkflow architecture" in text


def test_ui_boundary_is_documented():
    text = read_architecture()
    assert "User Interface Boundary" in text
    assert "The UI must NOT:" in text
    assert "authorize remediation" in text


def test_packaging_architecture_is_documented():
    text = read_architecture()
    assert "Packaging Architecture" in text
    assert "WindowsTechnician.exe" in text
    assert "_internal" in text


def test_packaging_lifecycle_is_documented():
    text = read_architecture()
    assert (
        "Build → Package → Validate → Install → Run → Upgrade → Run → Uninstall"
    ) in text


def test_documentation_architecture_is_documented():
    text = read_architecture()
    for path in (
        "docs/user/",
        "docs/technician/",
        "docs/architecture/",
        "docs/developer/",
        "docs/release/",
    ):
        assert path in text


def test_security_and_trust_are_documented():
    text = read_architecture()
    assert "Security and Trust" in text
    assert "explicit authorization" in text
    assert "evidence preservation" in text


def test_production_readiness_is_documented():
    text = read_architecture()
    assert "Production Readiness" in text
    assert "beta readiness" in text.lower()


def test_architectural_invariants_are_documented():
    text = read_architecture()
    assert "Architectural Invariants" in text
    assert "DiagnosticCase remains the canonical diagnostic case model." in text
    assert "TechnicianWorkflow remains the canonical technician workflow." in text


def test_architecture_is_documentation_not_implementation():
    text = read_architecture()
    assert "import " not in text
    assert "def " not in text
    assert "class " not in text
