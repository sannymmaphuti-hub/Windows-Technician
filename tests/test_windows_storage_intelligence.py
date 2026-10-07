# ==========================================
# Windows Technician v0.9
# STORAGE INTELLIGENCE TESTS
# ==========================================

import pytest

from engine.signal import Signal
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)
from engine.windows_storage_intelligence import (
    WindowsStorageIntelligence,
)


def make_evidence(*volumes):
    return WindowsStorageEvidence(
        volumes=list(volumes)
    )


# ==========================================
# CONSTRUCTION
# ==========================================


def test_storage_intelligence_can_be_created():
    intelligence = WindowsStorageIntelligence()

    assert intelligence is not None


def test_storage_intelligence_has_storage_domain():
    intelligence = WindowsStorageIntelligence()

    assert intelligence.domain == "STORAGE"


# ==========================================
# EMPTY / NORMAL STORAGE
# ==========================================


def test_empty_evidence_returns_empty_intelligence():
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        WindowsStorageEvidence()
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_healthy_volume_produces_no_storage_pressure_finding():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 500_000,
        }
    )

    result = intelligence.analyze(evidence)

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


# ==========================================
# WARNING STORAGE PRESSURE
# ==========================================


def test_low_free_space_produces_signal():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 1

    signal = result["signals"][0]

    assert isinstance(signal, Signal)
    assert signal.signal_type == "LOW_FREE_SPACE"
    assert signal.source == "STORAGE"
    assert signal.subject == "C:\\"
    assert signal.attribute == "free_space_ratio"


def test_low_free_space_signal_contains_ratio():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    result = intelligence.analyze(evidence)

    signal = result["signals"][0]

    assert signal.value == pytest.approx(0.10)


def test_low_free_space_produces_finding():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    result = intelligence.analyze(evidence)

    assert len(result["findings"]) == 1

    finding = result["findings"][0]

    assert isinstance(finding, Finding)
    assert finding.finding_type == "STORAGE_PRESSURE"
    assert finding.category == "STORAGE"
    assert finding.severity == "HIGH"


def test_low_free_space_finding_references_signal():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    result = intelligence.analyze(evidence)

    finding = result["findings"][0]

    assert len(finding.supporting_signals) == 1
    assert finding.supporting_signals[0] is result["signals"][0]


def test_low_free_space_produces_recommendation():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    result = intelligence.analyze(evidence)

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert isinstance(
        recommendation,
        Recommendation,
    )

    assert (
        recommendation.recommendation_type
        == "REVIEW_STORAGE_USAGE"
    )

    assert recommendation.category == "STORAGE"
    assert recommendation.priority == "HIGH"


# ==========================================
# CRITICAL STORAGE PRESSURE
# ==========================================


def test_critical_free_space_produces_critical_finding():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 30_000,
        }
    )

    result = intelligence.analyze(evidence)

    finding = result["findings"][0]

    assert finding.severity == "CRITICAL"


def test_critical_free_space_produces_critical_recommendation():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 30_000,
        }
    )

    result = intelligence.analyze(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation.priority == "CRITICAL"


# ==========================================
# MULTIPLE VOLUMES
# ==========================================


def test_multiple_volumes_are_evaluated_independently():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 500_000,
        },
        {
            "drive": "D:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 50_000,
        },
    )

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1

    assert result["signals"][0].subject == "D:\\"


def test_multiple_problem_volumes_produce_independent_signals():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 50_000,
        },
        {
            "drive": "D:\\",
            "total_bytes": 2_000_000,
            "free_bytes": 100_000,
        },
    )

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 2
    assert len(result["findings"]) == 2
    assert len(result["recommendations"]) == 2


# ==========================================
# INVALID EVIDENCE
# ==========================================


@pytest.mark.parametrize(
    "volume",
    [
        {
            "drive": "C:\\",
            "total_bytes": 0,
            "free_bytes": 0,
        },
        {
            "drive": "C:\\",
            "total_bytes": -1,
            "free_bytes": 1,
        },
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": -1,
        },
        {
            "drive": "C:\\",
            "total_bytes": "invalid",
            "free_bytes": 100,
        },
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": "invalid",
        },
    ],
)
def test_invalid_volume_data_is_ignored(volume):
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        make_evidence(volume)
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_missing_drive_is_ignored():
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        make_evidence(
            {
                "total_bytes": 1_000_000,
                "free_bytes": 10_000,
            }
        )
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_none_evidence_is_rejected():
    intelligence = WindowsStorageIntelligence()

    with pytest.raises(ValueError):
        intelligence.analyze(None)


# ==========================================
# RESULT ISOLATION
# ==========================================


def test_each_analysis_returns_fresh_result():
    intelligence = WindowsStorageIntelligence()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
    )

    first = intelligence.analyze(evidence)
    second = intelligence.analyze(evidence)

    assert first is not second
    assert first["signals"] is not second["signals"]
    assert first["findings"] is not second["findings"]
    assert (
        first["recommendations"]
        is not second["recommendations"]
    )


# ==========================================
# SAFETY BOUNDARIES
# ==========================================


def test_storage_intelligence_does_not_authorize_remediation():
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert "authorized" not in result
    assert "authorization" not in result


def test_storage_intelligence_does_not_execute_remediation():
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert "execution_status" not in result
    assert "remediation_result" not in result


def test_storage_intelligence_does_not_create_diagnostic_case():
    intelligence = WindowsStorageIntelligence()

    result = intelligence.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert "case_id" not in result
    assert "lifecycle_state" not in result


# ==========================================
# EVIDENCE IS NOT MUTATED
# ==========================================


def test_analysis_does_not_mutate_evidence():
    intelligence = WindowsStorageIntelligence()

    original_volume = {
        "drive": "C:\\",
        "total_bytes": 1_000_000,
        "free_bytes": 100_000,
    }

    evidence = make_evidence(
        original_volume
    )

    intelligence.analyze(evidence)

    assert evidence.volumes == [original_volume]