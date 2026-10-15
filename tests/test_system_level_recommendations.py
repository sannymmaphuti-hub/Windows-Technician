# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL RECOMMENDATIONS TESTS
# ==========================================

import pytest

from engine.system_level_recommendations import (
    SystemLevelRecommendations,
)


@pytest.fixture
def recommendations():
    return SystemLevelRecommendations()


def test_empty_system_data_returns_no_recommendations(
    recommendations,
):
    result = recommendations.generate({})

    assert result == {
        "recommendations": [],
        "recommendation_count": 0,
    }


def test_none_system_data_returns_no_recommendations(
    recommendations,
):
    result = recommendations.generate(None)

    assert result == {
        "recommendations": [],
        "recommendation_count": 0,
    }


def test_non_dict_system_data_is_rejected(
    recommendations,
):
    with pytest.raises(ValueError):
        recommendations.generate([])


def test_warning_finding_generates_recommendation(
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

    assert len(result["recommendations"]) == 1


def test_recommendation_preserves_domain(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "memory",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    recommendation = result["recommendations"][0]

    assert recommendation["domain"] == "MEMORY"


def test_recommendation_preserves_finding(
    recommendations,
):
    finding = {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }

    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": finding,
                }
            ]
        }
    )

    assert result["recommendations"][0]["finding"] == finding


def test_critical_finding_generates_high_priority_recommendation(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "SYSTEM",
                    "finding": {
                        "finding_type": "SYSTEM_FAILURE",
                        "severity": "CRITICAL",
                    },
                }
            ]
        }
    )

    assert result["recommendations"][0]["priority"] == "HIGH"


def test_error_finding_generates_high_priority_recommendation(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "SYSTEM",
                    "finding": {
                        "finding_type": "SYSTEM_FAILURE",
                        "severity": "ERROR",
                    },
                }
            ]
        }
    )

    assert result["recommendations"][0]["priority"] == "HIGH"


def test_warning_finding_generates_medium_priority_recommendation(
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

    assert result["recommendations"][0]["priority"] == "MEDIUM"


def test_medium_finding_generates_medium_priority_recommendation(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "HIGH_PROCESS_MEMORY",
                        "severity": "MEDIUM",
                    },
                }
            ]
        }
    )

    assert result["recommendations"][0]["priority"] == "MEDIUM"


def test_low_finding_generates_low_priority_recommendation(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "PROCESS_ACTIVITY",
                        "severity": "LOW",
                    },
                }
            ]
        }
    )

    assert result["recommendations"][0]["priority"] == "LOW"


def test_recommendations_are_sorted_by_priority(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "PROCESS_ACTIVITY",
                        "severity": "LOW",
                    },
                },
                {
                    "domain": "MEMORY",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                },
                {
                    "domain": "SYSTEM",
                    "finding": {
                        "finding_type": "SYSTEM_FAILURE",
                        "severity": "CRITICAL",
                    },
                },
            ]
        }
    )

    priorities = [
        recommendation["priority"]
        for recommendation in result["recommendations"]
    ]

    assert priorities == [
        "HIGH",
        "MEDIUM",
        "LOW",
    ]


def test_recommendation_has_action(
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

    assert recommendation["action"].strip()


def test_recommendation_has_rationale(
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

    assert recommendation["rationale"].strip()


def test_recommendation_has_priority(
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

    assert result["recommendations"][0]["priority"]


def test_memory_pressure_recommendation_is_investigative(
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

    action = result["recommendations"][0]["action"].lower()

    assert (
        "review" in action
        or "investigate" in action
        or "identify" in action
        or "monitor" in action
    )


def test_high_process_memory_recommendation_identifies_process(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "HIGH_PROCESS_MEMORY",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    action = result["recommendations"][0]["action"].lower()

    assert (
        "process" in action
        or "memory" in action
    )


def test_service_failure_recommendation_is_investigative(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "SERVICE",
                    "finding": {
                        "finding_type": "SERVICE_FAILURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    action = result["recommendations"][0]["action"].lower()

    assert (
        "service" in action
        or "review" in action
        or "investigate" in action
    )


def test_network_degradation_recommendation_is_investigative(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "NETWORK",
                    "finding": {
                        "finding_type": (
                            "NETWORK_CONNECTIVITY_DEGRADED"
                        ),
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    action = result["recommendations"][0]["action"].lower()

    assert (
        "network" in action
        or "connectivity" in action
        or "review" in action
        or "investigate" in action
    )


def test_system_resource_pressure_pattern_generates_high_priority_recommendation(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "confidence": "MEDIUM",
                    "domains": [
                        "MEMORY",
                        "PROCESS",
                    ],
                    "findings": [
                        {
                            "finding_type": "MEMORY_PRESSURE",
                            "severity": "WARNING",
                        },
                        {
                            "finding_type": (
                                "HIGH_PROCESS_MEMORY"
                            ),
                            "severity": "WARNING",
                        },
                    ],
                }
            ]
        }
    )

    assert len(result["recommendations"]) == 1
    assert (
        result["recommendations"][0]["priority"]
        == "MEDIUM"
    )


def test_pattern_recommendation_preserves_pattern(
    recommendations,
):
    pattern = {
        "type": "SYSTEM_RESOURCE_PRESSURE",
        "confidence": "MEDIUM",
        "domains": [
            "MEMORY",
            "PROCESS",
        ],
    }

    result = recommendations.generate(
        {
            "patterns": [pattern],
        }
    )

    assert (
        result["recommendations"][0]["pattern"]
        == pattern
    )


def test_pattern_recommendation_preserves_multiple_domains(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "domains": [
                        "memory",
                        "process",
                    ],
                }
            ]
        }
    )

    assert result["recommendations"][0]["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_multiple_finding_recommendations_are_preserved(
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
                },
                {
                    "domain": "SERVICE",
                    "finding": {
                        "finding_type": "SERVICE_FAILURE",
                        "severity": "WARNING",
                    },
                },
            ]
        }
    )

    assert len(result["recommendations"]) == 2


def test_multiple_patterns_are_preserved(
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
                },
                {
                    "type": "SERVICE_NETWORK_DEGRADATION",
                    "domains": [
                        "SERVICE",
                        "NETWORK",
                    ],
                },
            ]
        }
    )

    assert len(result["recommendations"]) == 2


def test_malformed_findings_are_ignored(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                None,
                "invalid",
                {},
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

    assert result["recommendation_count"] == 0


def test_malformed_patterns_are_ignored(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": [
                None,
                "invalid",
                {},
                {
                    "domains": [
                        "MEMORY",
                    ],
                },
            ]
        }
    )

    assert result["recommendation_count"] == 0


def test_non_list_findings_are_ignored(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": "invalid",
        }
    )

    assert result["recommendation_count"] == 0


def test_non_list_patterns_are_ignored(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": "invalid",
        }
    )

    assert result["recommendation_count"] == 0


def test_domain_names_are_normalized(
    recommendations,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": " memory ",
                    "finding": {
                        "finding_type": "MEMORY_PRESSURE",
                        "severity": "WARNING",
                    },
                }
            ]
        }
    )

    assert (
        result["recommendations"][0]["domain"]
        == "MEMORY"
    )


def test_pattern_types_are_normalized(
    recommendations,
):
    result = recommendations.generate(
        {
            "patterns": [
                {
                    "type": " system_resource_pressure ",
                    "domains": [
                        "memory",
                        "process",
                    ],
                }
            ]
        }
    )

    assert (
        result["recommendations"][0]["pattern"]["type"]
        == "SYSTEM_RESOURCE_PRESSURE"
    )


def test_input_is_not_mutated(
    recommendations,
):
    system_data = {
        "findings": [
            {
                "domain": "memory",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ],
        "patterns": [],
    }

    original = {
        "findings": [
            {
                "domain": "memory",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ],
        "patterns": [],
    }

    recommendations.generate(system_data)

    assert system_data == original


def test_result_contains_only_expected_keys(
    recommendations,
):
    result = recommendations.generate({})

    assert set(result.keys()) == {
        "recommendations",
        "recommendation_count",
    }


def test_result_does_not_contain_root_cause(
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

    assert "root_causes" not in result
    assert "primary_root_cause" not in result


def test_result_does_not_authorize_remediation(
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

    assert "remediation" not in result
    assert "authorized" not in result


def test_recommendation_does_not_claim_definite_causality(
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

    assert "definitely" not in text
    assert "certainly" not in text
    assert "proves" not in text
    assert "confirmed root cause" not in text
def test_finding_recommendation_exposes_traceable_evidence():
    finding = {
        "id": "memory-finding-001",
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
        "evidence": [{"source": "memory_monitor", "value": 92}],
        "provenance": {"collector": "memory_engine"},
    }

    result = SystemLevelRecommendations().generate({
        "findings": [{"domain": "MEMORY", "finding": finding}],
    })

    recommendation = result["recommendations"][0]

    assert recommendation["finding"] == finding
    assert recommendation.get("finding_id") == "memory-finding-001"
    assert recommendation.get("evidence") == finding["evidence"]
    assert recommendation.get("provenance") == finding["provenance"]


def test_finding_traceability_preserves_distinct_finding_ids():
    findings = [
        {
            "domain": "MEMORY",
            "finding": {
                "id": finding_id,
                "finding_type": "MEMORY_PRESSURE",
                "severity": "WARNING",
                "evidence": [{"source": "memory_monitor", "value": value}],
            },
        }
        for finding_id, value in (
            ("memory-001", 90),
            ("memory-002", 95),
        )
    ]

    result = SystemLevelRecommendations().generate({"findings": findings})
    recommendations = result["recommendations"]

    assert len(recommendations) == 2
    assert {item.get("finding_id") for item in recommendations} == {
        "memory-001",
        "memory-002",
    }

@pytest.mark.parametrize(
    "finding",
    [
        {
            "finding_type": "MEMORY_PRESSURE",
        },
        {
            "finding_type": "MEMORY_PRESSURE",
            "severity": "URGENT_UNKNOWN",
        },
    ],
    ids=["missing-severity", "unrecognized-severity"],
)
def test_unassessed_severity_is_explicit_in_recommendation(
    recommendations,
    finding,
):
    result = recommendations.generate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": finding,
                }
            ],
            "patterns": [],
        }
    )

    recommendation = next(
        item
        for item in result["recommendations"]
        if item["type"] == "FINDING"
    )

    assert recommendation["priority"] == "LOW"
    assert recommendation["severity_assessment"] == "UNASSESSED"
    assert "severity is unassessed" in recommendation["rationale"].lower()


def test_known_severity_is_marked_assessed(
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
            ],
            "patterns": [],
        }
    )

    recommendation = next(
        item
        for item in result["recommendations"]
        if item["type"] == "FINDING"
    )

    assert recommendation["priority"] == "MEDIUM"
    assert recommendation["severity_assessment"] == "ASSESSED"

@pytest.mark.parametrize(
    "pattern",
    [
        {
            "type": "SYSTEM_RESOURCE_PRESSURE",
            "domains": ["MEMORY", "PROCESS"],
        },
        {
            "type": "SYSTEM_RESOURCE_PRESSURE",
            "confidence": "UNRECOGNIZED",
            "domains": ["MEMORY", "PROCESS"],
        },
    ],
    ids=["missing-confidence", "unknown-confidence"],
)
def test_unassessed_pattern_confidence_is_explicit(
    recommendations,
    pattern,
):
    result = recommendations.generate({"patterns": [pattern]})
    recommendation = next(
        item
        for item in result["recommendations"]
        if item["type"] == "SYSTEM_PATTERN"
    )

    assert recommendation["priority"] == "LOW"
    assert recommendation["confidence_assessment"] == "UNASSESSED"
    assert recommendation["pattern"] == pattern
    assert "confidence is unassessed" in recommendation["rationale"].lower()

    if "confidence" not in pattern:
        assert "confidence" not in recommendation


def test_assessed_pattern_confidence_is_preserved(recommendations):
    pattern = {
        "type": "SYSTEM_RESOURCE_PRESSURE",
        "confidence": "MEDIUM",
        "domains": ["MEMORY", "PROCESS"],
    }

    result = recommendations.generate({"patterns": [pattern]})
    recommendation = next(
        item
        for item in result["recommendations"]
        if item["type"] == "SYSTEM_PATTERN"
    )

    assert recommendation["confidence"] == "MEDIUM"
    assert recommendation["confidence_assessment"] == "ASSESSED"
    assert recommendation["priority"] == "MEDIUM"
    assert recommendation["pattern"] == pattern
