"""Tests for the v0.9 documentation architecture."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"


EXPECTED_DOCUMENTS = (
    DOCS_ROOT / "README.md",
    DOCS_ROOT / "user" / "user_guide.md",
    DOCS_ROOT / "user" / "installation.md",
    DOCS_ROOT / "user" / "troubleshooting.md",
    DOCS_ROOT / "technician" / "technician_guide.md",
    DOCS_ROOT / "architecture" / "v0.9_architecture.md",
    DOCS_ROOT / "developer" / "developer_guide.md",
    DOCS_ROOT / "release" / "deployment.md",
)


def test_documentation_root_exists():
    assert DOCS_ROOT.is_dir()


def test_documentation_structure_exists():
    for path in (
        DOCS_ROOT / "user",
        DOCS_ROOT / "technician",
        DOCS_ROOT / "architecture",
        DOCS_ROOT / "developer",
        DOCS_ROOT / "release",
    ):
        assert path.is_dir()


def test_canonical_documents_exist():
    for document in EXPECTED_DOCUMENTS:
        assert document.is_file(), document


def test_documentation_index_references_all_guides():
    index = (DOCS_ROOT / "README.md").read_text(
        encoding="utf-8"
    )

    for document in EXPECTED_DOCUMENTS[1:]:
        relative = document.relative_to(DOCS_ROOT).as_posix()
        assert relative in index


def test_architecture_contains_canonical_intelligence_chain():
    architecture = (
        DOCS_ROOT / "architecture" / "v0.9_architecture.md"
    ).read_text(encoding="utf-8")

    assert (
        "Observation → Signal → Correlation → Finding → "
        "Root Cause → Explanation → Recommendation → Diagnostic Case"
    ) in architecture


def test_architecture_contains_canonical_remediation_chain():
    architecture = (
        DOCS_ROOT / "architecture" / "v0.9_architecture.md"
    ).read_text(encoding="utf-8")

    assert (
        "Eligibility → Decision → Authorization → Execution → Verification"
    ) in architecture


def test_release_document_describes_verified_lifecycle():
    deployment = (
        DOCS_ROOT / "release" / "deployment.md"
    ).read_text(encoding="utf-8")

    assert (
        "Build → Package → Validate → Install → Run → Upgrade → Run → Uninstall"
    ) in deployment


def test_user_documentation_does_not_define_internal_architecture():
    user_guide = (
        DOCS_ROOT / "user" / "user_guide.md"
    ).read_text(encoding="utf-8")

    assert "Canonical intelligence chain" not in user_guide
