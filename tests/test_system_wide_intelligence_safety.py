# ==========================================
# Windows Technician v0.9
# SYSTEM-WIDE INTELLIGENCE SAFETY TESTS
# ==========================================

import copy

import pytest

from engine.system_wide_intelligence import (
    SystemWideIntelligence,
)
from engine.cross_domain_system_evidence import (
    CrossDomainSystemEvidence,
)
from engine.system_problem_relationships import (
    SystemProblemRelationships,
)
from engine.system_root_cause_reasoning import (
    SystemRootCauseReasoning,
)
from engine.system_health_model import (
    SystemHealthModel,
)
from engine.system_wide_problem_correlation import (
    SystemWideProblemCorrelation,
)
from engine.system_level_investigation import (
    SystemLevelInvestigation,
)
from engine.system_level_recommendations import (
    SystemLevelRecommendations,
)


# ==========================================
# FIXTURES
# ==========================================


@pytest.fixture
def intelligence():
    return SystemWideIntelligence()


@pytest.fixture
def evidence_builder():
    return CrossDomainSystemEvidence()


@pytest.fixture
def relationships():
    return SystemProblemRelationships()


@pytest.fixture
def root_cause():
    return SystemRootCauseReasoning()


@pytest.fixture
def health():
    return SystemHealthModel()


@pytest.fixture
def correlation():
    return SystemWideProblemCorrelation()


@pytest.fixture
def investigation():
    return SystemLevelInvestigation()


@pytest.fixture
def recommendations():
    return SystemLevelRecommendations()


@pytest.fixture
def system_data():
    return {
        "MEMORY": {
            "findings": [
                {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                }
            ]
        },
        "PROCESS": {
            "findings": [
                {
                    "finding_type": "HIGH_PROCESS_MEMORY",
                    "severity": "WARNING",
                }
            ]
        },
    }


# ==========================================
# 6.9.1 INPUT VALIDATION
# ==========================================


@pytest.mark.parametrize(
    "value",
    [
        [],
        (),
        "invalid",
        123,
        1.5,
        True,
        False,
        object(),
    ],
)
def test_system_wide_intelligence_rejects_invalid_domain_mapping(
    intelligence,
    value,
):
    with pytest.raises(ValueError):
        intelligence.analyze(value)


@pytest.mark.parametrize(
    "value",
    [
        {},
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_cross_domain_evidence_rejects_invalid_domain_mapping(
    evidence_builder,
    value,
):
    if isinstance(value, dict):
        result = evidence_builder.collect(value)
        assert result["evidence"] == []
        return

    with pytest.raises(ValueError):
        evidence_builder.collect(value)


@pytest.mark.parametrize(
    "value",
    [
        {},
        "invalid",
        123,
        True,
        object(),
    ],
)
def test_relationship_layer_rejects_invalid_evidence(
    relationships,
    value,
):
    with pytest.raises(ValueError):
        relationships.analyze(value)


@pytest.mark.parametrize(
    "value",
    [
        {},
        "invalid",
        123,
        True,
        object(),
    ],
)
def test_root_cause_layer_rejects_invalid_relationships(
    root_cause,
    value,
):
    with pytest.raises(ValueError):
        root_cause.analyze(value)


def test_correlation_layer_accepts_empty_evidence(
    correlation,
):
    result = correlation.analyze([])

    assert result == {
        "patterns": [],
        "pattern_count": 0,
    }


@pytest.mark.parametrize(
    "value",
    [
        (),
        "invalid",
        123,
        True,
    ],
)
def test_correlation_layer_rejects_invalid_evidence(
    correlation,
    value,
):
    with pytest.raises(ValueError):
        correlation.analyze(value)

@pytest.mark.parametrize(
    "value",
    [
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_investigation_layer_rejects_invalid_system_data(
    investigation,
    value,
):
    with pytest.raises(ValueError):
        investigation.investigate(value)


@pytest.mark.parametrize(
    "value",
    [
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_recommendation_layer_rejects_invalid_system_data(
    recommendations,
    value,
):
    with pytest.raises(ValueError):
        recommendations.generate(value)


# ==========================================
# 6.9.2 NO FALSE ROOT CAUSE
# ==========================================


def test_empty_evidence_cannot_create_root_cause(
    root_cause,
):
    result = root_cause.analyze([])

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None
    assert result["confidence"] == "NONE"


def test_unrelated_findings_cannot_create_root_cause(
    relationships,
    root_cause,
):
    evidence = [
        {
            "domain": "PROCESS",
            "finding": "PROCESS_ACTIVITY",
        },
        {
            "domain": "NETWORK",
            "finding": "NETWORK_ACTIVITY",
        },
    ]

    relationship_result = relationships.analyze(
        evidence
    )

    root_result = root_cause.analyze(
        relationship_result["relationships"]
    )

    assert root_result["root_causes"] == []
    assert root_result["primary_root_cause"] is None


def test_unsupported_relationship_cannot_create_root_cause(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "UNSUPPORTED_RELATIONSHIP",
                "confidence": "HIGH",
            }
        ]
    )

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None


def test_low_confidence_relationship_stays_low_confidence(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "RESOURCE_INTERACTION",
                "confidence": "LOW",
            }
        ]
    )

    assert len(result["root_causes"]) == 1
    assert (
        result["root_causes"][0]["confidence"]
        == "LOW"
    )


def test_medium_confidence_relationship_stays_medium_confidence(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "RESOURCE_INTERACTION",
                "confidence": "MEDIUM",
            }
        ]
    )

    assert (
        result["root_causes"][0]["confidence"]
        == "MEDIUM"
    )


def test_unknown_confidence_does_not_become_high(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "RESOURCE_INTERACTION",
                "confidence": "UNKNOWN",
            }
        ]
    )

    assert (
        result["root_causes"][0]["confidence"]
        != "HIGH"
    )


def test_root_cause_explanation_does_not_claim_certainty(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "RESOURCE_INTERACTION",
                "confidence": "MEDIUM",
            }
        ]
    )

    explanation = (
        result["root_causes"][0]["explanation"]
        .lower()
    )

    assert "definitely" not in explanation
    assert "certainly" not in explanation
    assert "proves" not in explanation
    assert "confirmed" not in explanation


# ==========================================
# 6.9.3 CORRELATION ≠ CAUSATION
# ==========================================


def test_correlation_does_not_create_root_cause(
    correlation,
    root_cause,
):
    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "severity": "WARNING",
            },
        },
        {
            "domain": "PROCESS",
            "finding": {
                "finding_type": "HIGH_PROCESS_MEMORY",
                "severity": "WARNING",
            },
        },
    ]

    correlation_result = correlation.analyze(
        evidence
    )

    assert correlation_result["patterns"]

    root_result = root_cause.analyze(
        correlation_result["patterns"]
    )

    assert root_result["root_causes"] == []
    assert root_result["primary_root_cause"] is None


def test_relationship_does_not_automatically_mean_causation(
    relationships,
):
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

    result = relationships.analyze(
        evidence
    )

    relationship = result["relationships"][0]

    assert relationship["type"] == (
        "RESOURCE_INTERACTION"
    )

    assert "cause" not in relationship
    assert "root_cause" not in relationship


def test_correlation_pattern_does_not_claim_causation(
    correlation,
):
    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "severity": "WARNING",
            },
        },
        {
            "domain": "PROCESS",
            "finding": {
                "finding_type": "HIGH_PROCESS_MEMORY",
                "severity": "WARNING",
            },
        },
    ]

    result = correlation.analyze(evidence)

    pattern = result["patterns"][0]

    assert "root_cause" not in pattern
    assert "cause" not in pattern


# ==========================================
# 6.9.4 NO UNSUPPORTED REMEDIATION
# ==========================================


def test_recommendations_do_not_authorize_remediation(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    recommendation = result["recommendations"][0]

    assert "authorized" not in recommendation
    assert "execute" not in (
        recommendation["action"].lower()
    )
    assert "remediation" not in (
        recommendation["action"].lower()
    )


def test_pattern_recommendation_does_not_execute_changes(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "domains": [
                        "MEMORY",
                        "PROCESS",
                    ],
                }
            ]
        }
    )

    recommendation = result["recommendations"][0]

    text = (
        recommendation["action"]
        + recommendation["rationale"]
    ).lower()

    assert "execute" not in text
    assert "delete" not in text
    assert "terminate" not in text
    assert "kill process" not in text
    assert "disable service" not in text


# ==========================================
# 6.9.5 INVESTIGATION SAFETY
# ==========================================


def test_investigation_does_not_claim_root_cause(
    investigation,
):
    result = investigation.investigate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    target = result["targets"][0]

    assert "root cause" not in (
        target["question"].lower()
    )


def test_investigation_does_not_claim_certainty(
    investigation,
):
    result = investigation.investigate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    question = result["targets"][0][
        "question"
    ].lower()

    assert "definitely" not in question
    assert "certainly" not in question
    assert "proves" not in question


def test_investigation_does_not_authorize_remediation(
    investigation,
):
    result = investigation.investigate(
        {
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "domains": [
                        "MEMORY",
                        "PROCESS",
                    ],
                }
            ]
        }
    )

    target = result["targets"][0]

    assert "remediation" not in target
    assert "authorized" not in target


# ==========================================
# 6.9.6 HEALTH MODEL SAFETY
# ==========================================


def test_empty_health_state_is_incomplete(
    health,
):
    result = health.evaluate({})

    assert result["status"] == "INCOMPLETE"
    assert result["coverage"] == "NONE"


def test_health_model_does_not_create_root_cause(
    health,
):
    result = health.evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    }
                ]
            }
        }
    )

    assert "root_causes" not in result
    assert "primary_root_cause" not in result


def test_health_model_does_not_create_recommendations(
    health,
):
    result = health.evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    }
                ]
            }
        }
    )

    assert "recommendations" not in result


def test_health_score_never_exceeds_100(
    health,
):
    result = health.evaluate(
        {
            "MEMORY": {
                "findings": []
            }
        }
    )

    assert 0 <= result["health_score"] <= 100


def test_health_score_never_goes_below_zero(
    health,
):
    findings = [
        {
            "finding_type": f"CRITICAL_{index}",
            "severity": "CRITICAL",
        }
        for index in range(20)
    ]

    result = health.evaluate(
        {
            "SYSTEM": {
                "findings": findings
            }
        }
    )

    assert result["health_score"] >= 0


# ==========================================
# 6.9.7 IMMUTABILITY
# ==========================================


def test_system_wide_intelligence_does_not_mutate_input(
    intelligence,
    system_data,
):
    original = copy.deepcopy(
        system_data
    )

    intelligence.analyze(system_data)

    assert system_data == original


def test_evidence_builder_does_not_mutate_input(
    evidence_builder,
    system_data,
):
    original = copy.deepcopy(
        system_data
    )

    evidence_builder.collect(system_data)

    assert system_data == original


def test_relationship_layer_does_not_mutate_input(
    relationships,
):
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

    original = copy.deepcopy(evidence)

    relationships.analyze(evidence)

    assert evidence == original


def test_root_cause_layer_does_not_mutate_input(
    root_cause,
):
    relationships_data = [
        {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": [
                "MEMORY",
                "PROCESS",
            ],
        }
    ]

    original = copy.deepcopy(
        relationships_data
    )

    root_cause.analyze(
        relationships_data
    )

    assert relationships_data == original


def test_correlation_layer_does_not_mutate_input(
    correlation,
):
    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "severity": "WARNING",
            },
        },
        {
            "domain": "PROCESS",
            "finding": {
                "finding_type": "HIGH_PROCESS_MEMORY",
                "severity": "WARNING",
            },
        },
    ]

    original = copy.deepcopy(evidence)

    correlation.analyze(evidence)

    assert evidence == original


def test_investigation_layer_does_not_mutate_input(
    investigation,
):
    data = {
        "findings": [
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ]
    }

    original = copy.deepcopy(data)

    investigation.investigate(data)

    assert data == original


def test_recommendation_layer_does_not_mutate_input(
    recommendations,
):
    data = {
        "findings": [
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ]
    }

    original = copy.deepcopy(data)

    recommendations.generate(data)

    assert data == original


# ==========================================
# 6.9.8 MALFORMED CROSS-DOMAIN DATA
# ==========================================


def test_malformed_domain_payload_does_not_crash(
    intelligence,
):
    result = intelligence.analyze(
        {
            "MEMORY": None,
            "PROCESS": "invalid",
            "NETWORK": [],
            "SERVICE": {},
        }
    )

    assert result["status"] == "PARTIAL"
    assert result["domains"] == ["SERVICE"]


def test_malformed_evidence_items_are_ignored(
    relationships,
):
    result = relationships.analyze(
        [
            None,
            {},
            "invalid",
            {
                "domain": "",
                "finding": "MEMORY_PRESSURE",
            },
            {
                "domain": "MEMORY",
            },
        ]
    )

    assert result["relationships"] == []


def test_malformed_correlation_findings_are_ignored(
    correlation,
):
    result = correlation.analyze(
        [
            None,
            {},
            {
                "domain": "MEMORY",
                "finding": None,
            },
            {
                "domain": "PROCESS",
                "finding": "invalid",
            },
        ]
    )

    assert result["patterns"] == []


def test_malformed_investigation_findings_are_ignored(
    investigation,
):
    result = investigation.investigate(
        {
            "findings": [
                None,
                {},
                "invalid",
                {
                    "domain": "MEMORY",
                },
                {
                    "domain": "MEMORY",
                    "finding": None,
                },
            ]
        }
    )

    assert result["targets"] == []


def test_malformed_recommendation_findings_are_ignored(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                None,
                {},
                "invalid",
                {
                    "domain": "MEMORY",
                },
                {
                    "domain": "MEMORY",
                    "finding": None,
                },
            ]
        }
    )

    assert result["recommendations"] == []


# ==========================================
# 6.9.9 CONFIDENCE BOUNDARY
# ==========================================


def test_root_cause_cannot_upgrade_low_relationship_to_high(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "RESOURCE_INTERACTION",
                "confidence": "LOW",
            }
        ]
    )

    assert result["confidence"] == "LOW"


def test_root_cause_cannot_upgrade_medium_relationship_to_high(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "SERVICE_INTERACTION",
                "confidence": "MEDIUM",
            }
        ]
    )

    assert result["confidence"] == "MEDIUM"


def test_unknown_confidence_is_not_treated_as_high(
    root_cause,
):
    result = root_cause.analyze(
        [
            {
                "type": "SERVICE_INTERACTION",
                "confidence": "UNKNOWN",
            }
        ]
    )

    assert result["confidence"] != "HIGH"


# ==========================================
# 6.9.10 NO AUTOMATIC ACTION CHAIN
# ==========================================


def test_system_wide_intelligence_does_not_generate_actions(
    intelligence,
):
    result = intelligence.analyze(
        {
            "MEMORY": {
                "findings": [
                    {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    }
                ]
            }
        }
    )

    assert result["recommendations"] == []
    assert result["remediation"] is None


def test_evidence_layer_does_not_generate_actions(
    evidence_builder,
    system_data,
):
    result = evidence_builder.collect(
        system_data
    )

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None


def test_relationship_layer_does_not_generate_actions(
    relationships,
):
    result = relationships.analyze(
        [
            {
                "domain": "MEMORY",
                "finding": "MEMORY_PRESSURE",
            },
            {
                "domain": "PROCESS",
                "finding": "HIGH_PROCESS_MEMORY",
            },
        ]
    )

    assert "recommendations" not in result
    assert "remediation" not in result


def test_correlation_layer_does_not_generate_actions(
    correlation,
):
    result = correlation.analyze(
        [
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            },
            {
                "domain": "PROCESS",
                "finding": {
                    "finding_type": "HIGH_PROCESS_MEMORY",
                    "severity": "WARNING",
                },
            },
        ]
    )

    assert "recommendations" not in result
    assert "remediation" not in result


# ==========================================
# 6.9.11 SAFE SYSTEM-WIDE PIPELINE
# ==========================================


def test_system_wide_pipeline_preserves_layer_boundaries(
    intelligence,
    evidence_builder,
    relationships,
    root_cause,
    health,
    correlation,
    investigation,
    recommendations,
    system_data,
):
    intelligence_result = intelligence.analyze(
        system_data
    )

    evidence_result = evidence_builder.collect(
        system_data
    )

    relationship_result = relationships.analyze(
        evidence_result["evidence"]
    )

    root_result = root_cause.analyze(
        relationship_result["relationships"]
    )

    health_result = health.evaluate(
        system_data
    )

    correlation_result = correlation.analyze(
        evidence_result["evidence"]
    )

    investigation_result = investigation.investigate(
        {
            "findings": evidence_result["evidence"],
            "patterns": correlation_result["patterns"],
        }
    )

    recommendation_result = (
        recommendations.generate(
            {
                "findings": evidence_result[
                    "evidence"
                ],
                "patterns": correlation_result[
                    "patterns"
                ],
            }
        )
    )

    assert intelligence_result[
        "root_causes"
    ] == []

    assert evidence_result[
        "root_causes"
    ] == []

    assert root_result[
        "primary_root_cause"
    ] is not None

    assert "recommendations" not in (
        relationship_result
    )

    assert "remediation" not in (
        correlation_result
    )

    assert health_result[
        "health_score"
    ] >= 0

    assert investigation_result[
        "target_count"
    ] >= 1

    assert recommendation_result[
        "recommendation_count"
    ] >= 1


def test_safe_pipeline_does_not_auto_execute_anything(
    intelligence,
    evidence_builder,
    relationships,
    root_cause,
    health,
    correlation,
    investigation,
    recommendations,
    system_data,
):
    intelligence_result = intelligence.analyze(
        system_data
    )

    evidence_result = evidence_builder.collect(
        system_data
    )

    relationship_result = relationships.analyze(
        evidence_result["evidence"]
    )

    root_result = root_cause.analyze(
        relationship_result["relationships"]
    )

    health_result = health.evaluate(
        system_data
    )

    correlation_result = correlation.analyze(
        evidence_result["evidence"]
    )

    investigation_result = investigation.investigate(
        {
            "findings": evidence_result["evidence"],
            "patterns": correlation_result["patterns"],
        }
    )

    recommendation_result = (
        recommendations.generate(
            {
                "findings": evidence_result[
                    "evidence"
                ],
                "patterns": correlation_result[
                    "patterns"
                ],
            }
        )
    )

    assert intelligence_result[
        "remediation"
    ] is None

    assert "remediation" not in (
        evidence_result
    )

    assert "remediation" not in (
        relationship_result
    )

    assert "remediation" not in (
        root_result
    )

    assert "remediation" not in (
        health_result
    )

    assert "remediation" not in (
        correlation_result
    )

    assert "remediation" not in (
        investigation_result
    )

    assert "remediation" not in (
        recommendation_result
    )
