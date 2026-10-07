# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL ROOT-CAUSE REASONING
# ==========================================

import pytest

from engine.system_root_cause_reasoning import (
    SystemRootCauseReasoning,
)


def test_empty_relationships_produce_no_root_cause():
    engine = SystemRootCauseReasoning()

    result = engine.analyze([])

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None
    assert result["confidence"] == "NONE"


def test_unrelated_relationship_does_not_create_fake_root_cause():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "UNRELATED",
            "confidence": "MEDIUM",
            "domains": [
                "NETWORK",
                "DISK",
            ],
            "findings": [
                "NETWORK_DEGRADED",
                "LOW_FREE_SPACE",
            ],
        }
    ]

    result = engine.analyze(relationships)

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None
    assert result["confidence"] == "NONE"


def test_resource_interaction_produces_root_cause_candidate():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    assert len(result["root_causes"]) == 1

    candidate = result["root_causes"][0]

    assert candidate["cause_type"] == (
        "PROCESS_RESOURCE_CONSUMPTION"
    )


def test_root_cause_preserves_supporting_relationship():
    engine = SystemRootCauseReasoning()

    relationship = {
        "type": "RESOURCE_INTERACTION",
        "confidence": "MEDIUM",
        "domains": [
            "MEMORY",
            "PROCESS",
        ],
        "findings": [
            "MEMORY_PRESSURE",
            "HIGH_PROCESS_MEMORY",
        ],
    }

    result = engine.analyze(
        [relationship]
    )

    candidate = result["root_causes"][0]

    assert candidate["supporting_relationships"] == [
        relationship
    ]


def test_root_cause_has_confidence():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    candidate = result["root_causes"][0]

    assert candidate["confidence"] == "MEDIUM"


def test_root_cause_has_explanation():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    candidate = result["root_causes"][0]

    assert candidate["explanation"]


def test_primary_root_cause_is_selected_when_supported():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "HIGH",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    assert result["primary_root_cause"] is not None
    assert (
        result["primary_root_cause"]["cause_type"]
        == "PROCESS_RESOURCE_CONSUMPTION"
    )


def test_low_confidence_relationship_does_not_become_high_confidence_root_cause():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "LOW",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    candidate = result["root_causes"][0]

    assert candidate["confidence"] == "LOW"


def test_multiple_candidates_are_preserved():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        },
        {
            "type": "SERVICE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "SERVICE",
                "NETWORK",
            ],
            "findings": [
                "SERVICE_FAILURE",
                "NETWORK_DEGRADED",
            ],
        },
    ]

    result = engine.analyze(relationships)

    assert len(result["root_causes"]) == 2


def test_primary_root_cause_does_not_hide_alternative_candidates():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "HIGH",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        },
        {
            "type": "SERVICE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "SERVICE",
                "NETWORK",
            ],
            "findings": [
                "SERVICE_FAILURE",
                "NETWORK_DEGRADED",
            ],
        },
    ]

    result = engine.analyze(relationships)

    assert result["primary_root_cause"] is not None
    assert len(result["root_causes"]) == 2


def test_relationship_does_not_become_certain_causality():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "HIGH",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    candidate = result["root_causes"][0]

    assert candidate["confidence"] != "CERTAIN"
    assert candidate["confidence"] == "HIGH"


def test_root_cause_has_no_remediation():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "HIGH",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    result = engine.analyze(relationships)

    candidate = result["root_causes"][0]

    assert "remediation" not in candidate


def test_input_is_not_mutated():
    engine = SystemRootCauseReasoning()

    relationships = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    original = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
            "findings": [
                "MEMORY_PRESSURE",
                "HIGH_PROCESS_MEMORY",
            ],
        }
    ]

    engine.analyze(relationships)

    assert relationships == original


def test_invalid_relationships_are_ignored():
    engine = SystemRootCauseReasoning()

    result = engine.analyze(
        [
            None,
            "invalid",
            {
                "type": "UNKNOWN",
                "confidence": "LOW",
                "domains": [],
                "findings": [],
            },
        ]
    )

    assert result["root_causes"] == []


def test_non_list_relationships_are_rejected():
    engine = SystemRootCauseReasoning()

    with pytest.raises(ValueError):
        engine.analyze(
            {
                "type": "RESOURCE_INTERACTION"
            }
        )


def test_result_has_stable_contract():
    engine = SystemRootCauseReasoning()

    result = engine.analyze([])

    assert set(result.keys()) == {
        "root_causes",
        "primary_root_cause",
        "confidence",
    }

