# ==========================================
# Windows Technician v0.9
# SYSTEM HEALTH MODEL TESTS
# ==========================================

import pytest

from engine.system_health_model import (
    SystemHealthModel,
)


def test_empty_system_is_incomplete():
    result = SystemHealthModel().evaluate()

    assert result["status"] == "INCOMPLETE"


def test_empty_system_has_zero_health_score():
    result = SystemHealthModel().evaluate()

    assert result["health_score"] == 0


def test_empty_system_has_no_domains():
    result = SystemHealthModel().evaluate()

    assert result["domains"] == []


def test_empty_system_has_no_findings():
    result = SystemHealthModel().evaluate()

    assert result["findings"] == []


def test_single_healthy_domain_is_healthy():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [],
            }
        }
    )

    assert result["status"] == "HEALTHY"


def test_single_healthy_domain_is_partial():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [],
            }
        }
    )

    assert result["coverage"] == "PARTIAL"


def test_multiple_healthy_domains_are_healthy():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [],
            },
            "PROCESS": {
                "findings": [],
            },
        }
    )

    assert result["status"] == "HEALTHY"


def test_warning_finding_produces_warning_health():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ],
            }
        }
    )

    assert result["status"] == "WARNING"


def test_critical_finding_produces_critical_health():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "finding_type": "MEMORY_EXHAUSTION",
                    }
                ],
            }
        }
    )

    assert result["status"] == "CRITICAL"


def test_error_severity_is_treated_as_critical():
    result = SystemHealthModel().evaluate(
        {
            "SYSTEM": {
                "findings": [
                    {
                        "severity": "ERROR",
                        "finding_type": "SYSTEM_FAILURE",
                    }
                ],
            }
        }
    )

    assert result["status"] == "CRITICAL"


def test_medium_finding_produces_degraded_health():
    result = SystemHealthModel().evaluate(
        {
            "PROCESS": {
                "findings": [
                    {
                        "severity": "MEDIUM",
                        "finding_type": "HIGH_PROCESS_MEMORY",
                    }
                ],
            }
        }
    )

    assert result["status"] == "DEGRADED"


def test_low_finding_does_not_make_system_critical():
    result = SystemHealthModel().evaluate(
        {
            "SYSTEM": {
                "findings": [
                    {
                        "severity": "LOW",
                        "finding_type": "MINOR_CONFIGURATION_ISSUE",
                    }
                ],
            }
        }
    )

    assert result["status"] in {
        "HEALTHY",
        "DEGRADED",
    }


def test_highest_severity_wins():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ],
            },
            "PROCESS": {
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "finding_type": "PROCESS_FAILURE",
                    }
                ],
            },
        }
    )

    assert result["status"] == "CRITICAL"


def test_domains_are_normalized():
    result = SystemHealthModel().evaluate(
        {
            " memory ": {
                "findings": [],
            },
            "Process": {
                "findings": [],
            },
        }
    )

    assert result["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_domain_health_is_preserved():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ],
            }
        }
    )

    assert result["domain_health"]["MEMORY"] == "WARNING"


def test_findings_preserve_domain_provenance():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ],
            }
        }
    )

    assert result["findings"][0]["domain"] == "MEMORY"


def test_findings_are_preserved():
    finding = {
        "severity": "WARNING",
        "finding_type": "MEMORY_PRESSURE",
    }

    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [finding],
            }
        }
    )

    assert result["findings"][0]["finding"] == finding


def test_health_score_is_bounded():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "finding_type": "MEMORY_EXHAUSTION",
                    }
                ]
                * 20,
            },
            "PROCESS": {
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "finding_type": "PROCESS_FAILURE",
                    }
                ]
                * 20,
            },
        }
    )

    assert 0 <= result["health_score"] <= 100


def test_critical_system_has_lower_score_than_healthy_system():
    healthy = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [],
            },
            "PROCESS": {
                "findings": [],
            },
        }
    )

    critical = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "finding_type": "MEMORY_EXHAUSTION",
                    }
                ],
            }
        }
    )

    assert critical["health_score"] < healthy["health_score"]


def test_healthy_system_has_full_health_score():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [],
            },
            "PROCESS": {
                "findings": [],
            },
        }
    )

    assert result["health_score"] == 100


def test_invalid_domain_mapping_is_rejected():
    with pytest.raises(ValueError):
        SystemHealthModel().evaluate(
            ["MEMORY"]
        )


def test_invalid_domain_payload_is_ignored():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": None,
            "PROCESS": {
                "findings": [],
            },
        }
    )

    assert result["domains"] == [
        "PROCESS"
    ]


def test_missing_findings_are_treated_as_empty():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {}
        }
    )

    assert result["status"] == "HEALTHY"


def test_non_list_findings_are_ignored():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": "MEMORY_PRESSURE",
            }
        }
    )

    assert result["status"] == "HEALTHY"


def test_unknown_severity_does_not_create_critical_health():
    result = SystemHealthModel().evaluate(
        {
            "SYSTEM": {
                "findings": [
                    {
                        "severity": "UNKNOWN",
                        "finding_type": "UNCLASSIFIED",
                    }
                ],
            }
        }
    )

    assert result["status"] != "CRITICAL"


def test_input_is_not_mutated():
    domains = {
        "MEMORY": {
            "findings": [
                {
                    "severity": "WARNING",
                    "finding_type": "MEMORY_PRESSURE",
                }
            ]
        }
    }

    original = {
        "MEMORY": {
            "findings": [
                {
                    "severity": "WARNING",
                    "finding_type": "MEMORY_PRESSURE",
                }
            ]
        }
    }

    SystemHealthModel().evaluate(domains)

    assert domains == original


def test_result_has_stable_contract():
    result = SystemHealthModel().evaluate()

    assert set(result.keys()) == {
        "status",
        "health_score",
        "coverage",
        "domains",
        "domain_health",
        "findings",
    }


def test_health_model_does_not_generate_root_causes():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ]
            }
        }
    )

    assert "root_causes" not in result


def test_health_model_does_not_generate_recommendations():
    result = SystemHealthModel().evaluate(
        {
            "MEMORY": {
                "findings": [
                    {
                        "severity": "WARNING",
                        "finding_type": "MEMORY_PRESSURE",
                    }
                ]
            }
        }
    )

    assert "recommendations" not in result



def test_duplicate_warning_is_penalized_once_but_findings_are_preserved():
    finding = {
        "severity": "WARNING",
        "finding_type": "MEMORY_PRESSURE",
        "message": "High memory usage.",
    }
    result = SystemHealthModel().evaluate({
        "PROCESS": {"findings": [finding]},
        "MEMORY": {"findings": [dict(finding)]},
    })
    assert result["health_score"] == 90
    assert len(result["findings"]) == 2


def test_distinct_warnings_each_reduce_health_score():
    result = SystemHealthModel().evaluate({
        "PROCESS": {"findings": [
            {"severity": "WARNING", "message": "High memory usage."}
        ]},
        "NETWORK": {"findings": [
            {"severity": "WARNING", "message": "Packet loss detected."}
        ]},
    })
    assert result["health_score"] == 80


def test_warning_and_high_penalties_are_calibrated():
    result = SystemHealthModel().evaluate({
        "SYSTEM": {"findings": [
            {"severity": "WARNING", "message": "Warning A"},
            {"severity": "HIGH", "message": "High A"},
        ]}
    })
    assert result["health_score"] == 70
