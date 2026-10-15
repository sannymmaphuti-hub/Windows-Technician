# ==========================================
# Windows Technician v0.9
# SYSTEM PROBLEM RELATIONSHIPS
# ==========================================

import pytest

from engine.system_problem_relationships import (
    SystemProblemRelationships,
)


def test_empty_evidence_produces_no_relationships():
    engine = SystemProblemRelationships()

    result = engine.analyze([])

    assert result["relationships"] == []
    assert result["relationship_count"] == 0


def test_single_evidence_item_produces_no_relationship():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        }
    ]

    result = engine.analyze(evidence)

    assert result["relationships"] == []
    assert result["relationship_count"] == 0


def test_memory_and_process_pressure_are_related():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    assert result["relationship_count"] == 1

    relationship = result["relationships"][0]

    assert relationship["domains"] == [
        "MEMORY",
        "PROCESS",
    ]

    assert relationship["findings"] == [
        "MEMORY_PRESSURE",
        "HIGH_PROCESS_MEMORY",
    ]


def test_relationship_has_explicit_type():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    relationship = result["relationships"][0]

    assert relationship["type"] == "RESOURCE_INTERACTION"


def test_relationship_has_confidence():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    relationship = result["relationships"][0]

    assert relationship["confidence"] == "MEDIUM"


def test_unrelated_domains_do_not_create_fake_relationships():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "NETWORK",
            "finding": "NETWORK_DEGRADED",
        },
        {
            "domain": "DISK",
            "finding": "LOW_FREE_SPACE",
        },
    ]

    result = engine.analyze(evidence)

    assert result["relationships"] == []


def test_relationship_does_not_claim_causality():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    relationship = result["relationships"][0]

    assert "cause" not in relationship
    assert "root_cause" not in relationship


def test_relationship_does_not_create_root_causes():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None


def test_multiple_related_findings_are_grouped():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_COMMIT_USAGE",
        },
    ]

    result = engine.analyze(evidence)

    assert result["relationship_count"] == 1

    relationship = result["relationships"][0]

    assert relationship["domains"] == [
        "MEMORY",
        "PROCESS",
    ]

    assert relationship["findings"] == [
        "MEMORY_PRESSURE",
        "HIGH_PROCESS_MEMORY",
        "HIGH_COMMIT_USAGE",
    ]


def test_duplicate_evidence_does_not_create_duplicate_relationship():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
    ]

    result = engine.analyze(evidence)

    assert result["relationship_count"] == 1


def test_relationship_preserves_finding_provenance():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    relationship = result["relationships"][0]

    assert relationship["evidence"] == evidence


def test_input_is_not_mutated():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    original = [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    engine.analyze(evidence)

    assert evidence == original


def test_invalid_evidence_is_ignored():
    engine = SystemProblemRelationships()

    result = engine.analyze(
        [
            None,
            "invalid",
            {
                "domain": "MEMORY",
                "finding": "MEMORY_PRESSURE",
            },
        ]
    )

    assert result["relationship_count"] == 0


def test_invalid_evidence_input_is_rejected():
    engine = SystemProblemRelationships()

    with pytest.raises(ValueError):
        engine.analyze(
            {
                "domain": "MEMORY",
                "finding": "MEMORY_PRESSURE",
            }
        )


def test_domain_names_are_normalized():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": " memory ",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": " process ",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]

    result = engine.analyze(evidence)

    relationship = result["relationships"][0]

    assert relationship["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_result_has_stable_contract():
    engine = SystemProblemRelationships()

    result = engine.analyze([])

    assert set(result.keys()) == {
        "relationships",
        "relationship_count",
        "root_causes",
        "primary_root_cause",
    }

def test_relationship_preserves_all_distinct_memory_evidence():
    engine = SystemProblemRelationships()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "finding_id": "memory-01",
            },
        },
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "finding_id": "memory-02",
            },
        },
        {
            "domain": "PROCESS",
            "finding": {
                "finding_type": "HIGH_PROCESS_MEMORY",
                "finding_id": "process-01",
            },
        },
    ]

    result = engine.analyze(evidence)

    assert result["relationship_count"] == 1

    relationship = result["relationships"][0]

    assert relationship["evidence"] == evidence
    assert [
        item["finding"]["finding_id"]
        for item in relationship["evidence"]
    ] == [
        "memory-01",
        "memory-02",
        "process-01",
    ]
