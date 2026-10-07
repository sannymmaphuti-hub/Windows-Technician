# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL INVESTIGATION TESTS
# ==========================================

import pytest

from engine.system_level_investigation import (
    SystemLevelInvestigation,
)


def test_empty_input_returns_no_investigation_targets():
    result = SystemLevelInvestigation().investigate()

    assert result["targets"] == []
    assert result["target_count"] == 0


def test_non_dict_input_is_rejected():
    with pytest.raises(ValueError):
        SystemLevelInvestigation().investigate(
            []
        )


def test_empty_system_data_returns_no_targets():
    result = SystemLevelInvestigation().investigate(
        {}
    )

    assert result["targets"] == []


def test_warning_finding_creates_investigation_target():
    result = SystemLevelInvestigation().investigate(
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

    assert len(result["targets"]) == 1


def test_target_preserves_domain():
    result = SystemLevelInvestigation().investigate(
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

    assert (
        result["targets"][0]["domain"]
        == "MEMORY"
    )


def test_target_preserves_finding():
    finding = {
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
    }

    result = SystemLevelInvestigation().investigate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": finding,
                }
            ]
        }
    )

    assert (
        result["targets"][0]["finding"]
        == finding
    )


def test_critical_finding_gets_high_priority():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [
                {
                    "domain": "MEMORY",
                    "finding": {
                        "finding_type": "MEMORY_EXHAUSTION",
                        "severity": "CRITICAL",
                    },
                }
            ]
        }
    )

    assert (
        result["targets"][0]["priority"]
        == "HIGH"
    )


def test_warning_finding_gets_medium_priority():
    result = SystemLevelInvestigation().investigate(
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

    assert (
        result["targets"][0]["priority"]
        == "MEDIUM"
    )


def test_medium_finding_gets_medium_priority():
    result = SystemLevelInvestigation().investigate(
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

    assert (
        result["targets"][0]["priority"]
        == "MEDIUM"
    )


def test_low_finding_gets_low_priority():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [
                {
                    "domain": "SYSTEM",
                    "finding": {
                        "finding_type": "MINOR_CONFIGURATION_ISSUE",
                        "severity": "LOW",
                    },
                }
            ]
        }
    )

    assert (
        result["targets"][0]["priority"]
        == "LOW"
    )


def test_targets_are_sorted_by_priority():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [
                {
                    "domain": "SYSTEM",
                    "finding": {
                        "finding_type": "MINOR_CONFIGURATION_ISSUE",
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
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "PROCESS_FAILURE",
                        "severity": "CRITICAL",
                    },
                },
            ]
        }
    )

    assert [
        target["priority"]
        for target in result["targets"]
    ] == [
        "HIGH",
        "MEDIUM",
        "LOW",
    ]


def test_investigation_question_is_present():
    result = SystemLevelInvestigation().investigate(
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

    assert isinstance(
        result["targets"][0]["question"],
        str,
    )

    assert result["targets"][0]["question"]


def test_investigation_question_is_not_a_root_cause_claim():
    result = SystemLevelInvestigation().investigate(
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

    question = (
        result["targets"][0]["question"]
        .lower()
    )

    assert "root cause" not in question
    assert "definitely" not in question


def test_relationship_creates_higher_priority_investigation():
    result = SystemLevelInvestigation().investigate(
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
                    "domain": "PROCESS",
                    "finding": {
                        "finding_type": "HIGH_PROCESS_MEMORY",
                        "severity": "WARNING",
                    },
                },
            ],
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "confidence": "MEDIUM",
                    "domains": [
                        "MEMORY",
                        "PROCESS",
                    ],
                }
            ],
        }
    )

    assert len(result["targets"]) >= 1

    assert any(
        target["priority"] == "HIGH"
        for target in result["targets"]
    )


def test_pattern_information_is_preserved():
    pattern = {
        "type": "SYSTEM_RESOURCE_PRESSURE",
        "confidence": "MEDIUM",
        "domains": [
            "MEMORY",
            "PROCESS",
        ],
    }

    result = SystemLevelInvestigation().investigate(
        {
            "findings": [],
            "patterns": [pattern],
        }
    )

    assert (
        result["targets"][0]["pattern"]
        == pattern
    )


def test_pattern_target_has_multiple_domains():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [],
            "patterns": [
                {
                    "type": "SYSTEM_RESOURCE_PRESSURE",
                    "confidence": "MEDIUM",
                    "domains": [
                        "MEMORY",
                        "PROCESS",
                    ],
                }
            ],
        }
    )

    assert result["targets"][0]["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_multiple_targets_are_preserved():
    result = SystemLevelInvestigation().investigate(
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
                    "domain": "NETWORK",
                    "finding": {
                        "finding_type": "NETWORK_CONNECTIVITY_DEGRADED",
                        "severity": "WARNING",
                    },
                },
            ]
        }
    )

    assert len(result["targets"]) == 2


def test_malformed_findings_are_ignored():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [
                None,
                "invalid",
                {},
                {
                    "domain": "MEMORY",
                },
            ]
        }
    )

    assert result["targets"] == []


def test_non_list_findings_are_ignored():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": "MEMORY_PRESSURE"
        }
    )

    assert result["targets"] == []


def test_non_list_patterns_are_ignored():
    result = SystemLevelInvestigation().investigate(
        {
            "findings": [],
            "patterns": "SYSTEM_RESOURCE_PRESSURE",
        }
    )

    assert result["targets"] == []


def test_domain_names_are_normalized():
    result = SystemLevelInvestigation().investigate(
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
        result["targets"][0]["domain"]
        == "MEMORY"
    )


def test_input_is_not_mutated():
    system_data = {
        "findings": [
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ],
        "patterns": [
            {
                "type": "SYSTEM_RESOURCE_PRESSURE",
                "confidence": "MEDIUM",
                "domains": [
                    "MEMORY",
                    "PROCESS",
                ],
            }
        ],
    }

    original = {
        "findings": [
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            }
        ],
        "patterns": [
            {
                "type": "SYSTEM_RESOURCE_PRESSURE",
                "confidence": "MEDIUM",
                "domains": [
                    "MEMORY",
                    "PROCESS",
                ],
            }
        ],
    }

    SystemLevelInvestigation().investigate(
        system_data
    )

    assert system_data == original


def test_result_has_stable_contract():
    result = SystemLevelInvestigation().investigate()

    assert set(result.keys()) == {
        "targets",
        "target_count",
    }


def test_investigation_does_not_generate_recommendations():
    result = SystemLevelInvestigation().investigate(
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

    assert "recommendations" not in result


def test_investigation_does_not_generate_remediation():
    result = SystemLevelInvestigation().investigate(
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


def test_investigation_does_not_select_root_cause():
    result = SystemLevelInvestigation().investigate(
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

