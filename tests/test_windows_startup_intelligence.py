# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP INTELLIGENCE TESTS
# ==========================================

from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)
from engine.windows_startup_intelligence import (
    WindowsStartupIntelligence,
)


def test_intelligence_has_startup_domain():
    intelligence = WindowsStartupIntelligence()

    assert intelligence.domain == "STARTUP"


def test_healthy_startup_item_produces_no_problem():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "OneDrive",
                "command": "OneDrive.exe",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_missing_command_creates_signal():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert len(result["signals"]) == 1

    signal = result["signals"][0]

    assert signal.signal_type == (
        "STARTUP_COMMAND_MISSING"
    )
    assert signal.source == "STARTUP"
    assert signal.subject == "BrokenStartup"
    assert signal.attribute == "command"
    assert signal.value == ""
    assert signal.strength == "MEDIUM"
    assert signal.quality == "HIGH"


def test_missing_command_creates_finding():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert len(result["findings"]) == 1

    finding = result["findings"][0]

    assert finding.finding_type == (
        "STARTUP_COMMAND_MISSING"
    )
    assert finding.category == "STARTUP"
    assert finding.severity == "MEDIUM"
    assert (
        finding.supporting_signals[0]
        is result["signals"][0]
    )


def test_missing_command_creates_recommendation():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert len(result["recommendations"]) == 1

    recommendation = (
        result["recommendations"][0]
    )

    assert recommendation.recommendation_type == (
        "REVIEW_STARTUP_ENTRY"
    )
    assert recommendation.category == "STARTUP"
    assert recommendation.priority == "MEDIUM"


def test_disabled_startup_item_is_not_automatically_problem():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "DisabledApp",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": False,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_multiple_items_only_problematic_items_are_reported():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "Healthy",
                "command": "Healthy.exe",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
            {
                "name": "Broken",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
            {
                "name": "Disabled",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": False,
            },
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1

    assert (
        result["signals"][0].subject
        == "Broken"
    )


def test_malformed_records_are_ignored():
    evidence = WindowsStartupEvidence(
        items=[
            "invalid",
            None,
            123,
            {
                "name": "Healthy",
                "command": "Healthy.exe",
                "enabled": True,
            },
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_empty_evidence_produces_empty_result():
    evidence = WindowsStartupEvidence()

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_invalid_evidence_is_rejected():
    try:
        WindowsStartupIntelligence().analyze(
            None
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid evidence."
    )


def test_recommendation_explains_missing_command():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    recommendation = (
        result["recommendations"][0]
    )

    assert (
        "BrokenStartup"
        in recommendation.description
    )

    assert (
        "command"
        in recommendation.rationale.lower()
    )


def test_enabled_value_must_be_true_for_problem_analysis():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "DisabledBroken",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": False,
            }
        ]
    )

    result = WindowsStartupIntelligence().analyze(
        evidence
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []