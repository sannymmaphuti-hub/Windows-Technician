from pathlib import Path


GUIDE = Path("docs/technician/technician_guide.md")


def read_guide() -> str:
    assert GUIDE.exists(), "Technician guide does not exist."
    return GUIDE.read_text(encoding="utf-8")


def test_technician_guide_exists():
    assert GUIDE.exists()


def test_technician_guide_contains_core_workflow():
    content = read_guide()

    required = [
        "# Windows Technician Technician Guide",
        "# 1. Technician Workflow",
        "# 2. Diagnostic Case",
        "# 5. Diagnostic Reasoning Chain",
        "# 10. Remediation Decision Boundary",
        "# 13. Verification",
        "# 16. Recovery",
        "# 18. Remote Diagnostics",
        "# 19. Proactive Cases",
        "# 20. Multi-Machine Operations",
        "# 23. Case Closure",
        "# 24. Escalation",
        "# 25. Safety Rules",
        "# 27. Technician Boundary",
    ]

    for section in required:
        assert section in content


def test_technician_guide_contains_canonical_reasoning_chain():
    content = read_guide()

    assert (
        "Observation → Signal → Correlation → Finding → Root Cause → "
        "Explanation → Recommendation"
    ) in content


def test_technician_guide_contains_remediation_boundary():
    content = read_guide()

    assert (
        "Eligibility → Decision → Authorization → Execution → Verification"
    ) in content


def test_technician_guide_separates_authorization_from_diagnosis():
    content = read_guide()

    assert "Authorization is separate from diagnosis." in content
    assert "The existence of a recommendation does not authorize execution." in content


def test_technician_guide_separates_execution_from_verification():
    content = read_guide()

    assert "Executed ≠ Verified" in content
    assert "A successful execution does not prove that the underlying problem has been resolved." in content


def test_technician_guide_rejects_blind_retry():
    content = read_guide()

    assert "Do not blindly retry the same remediation." in content
    assert "Recovery is not blind retry." in content


def test_technician_guide_documents_remote_and_proactive_workflows():
    content = read_guide()

    assert "Technician → RemoteSession → RemoteMachine → Diagnostic → Case → Decision → Remediation → Verification" in content
    assert "A proactive condition should still become a canonical diagnostic case." in content


def test_technician_guide_preserves_machine_and_case_boundaries():
    content = read_guide()

    assert "Which machine is being investigated." in content
    assert "Which case belongs to that machine." in content
    assert "Do not mix evidence between machines." in content


def test_technician_guide_contains_safety_and_escalation():
    content = read_guide()

    assert "# 24. Escalation" in content
    assert "# 25. Safety Rules" in content
    assert "Escalation is part of safe technician operation" in content


def test_technician_guide_protects_architecture_boundaries():
    content = read_guide()

    forbidden_architecture = [
        "The presentation layer must not independently:",
        "Diagnose",
        "Reason about root causes",
        "Create recommendations",
        "Authorize remediation",
        "Execute remediation",
        "Retry operations",
        "Verify remediation",
    ]

    for phrase in forbidden_architecture:
        assert phrase in content


def test_technician_guide_is_documentation_not_implementation():
    content = read_guide()

    forbidden = [
        "pytest",
        "test_technician_guide.py",
        "import PySide6",
    ]

    for phrase in forbidden:
        assert phrase not in content
