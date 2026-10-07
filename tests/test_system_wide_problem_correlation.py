# ==========================================
# Windows Technician v0.9
# SYSTEM-WIDE PROBLEM CORRELATION TESTS
# ==========================================

import pytest

from engine.system_wide_problem_correlation import (
    SystemWideProblemCorrelation,
)


def test_empty_findings_return_no_patterns():
    result = SystemWideProblemCorrelation().analyze([])

    assert result["patterns"] == []
    assert result["pattern_count"] == 0


def test_non_list_input_is_rejected():
    with pytest.raises(ValueError):
        SystemWideProblemCorrelation().analyze(
            {}
        )


def test_unrelated_findings_return_no_patterns():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": "SYSTEM",
                "finding": {
                    "finding_type": "SYSTEM_INFORMATION_MISSING",
                    "severity": "MEDIUM",
                },
            },
            {
                "domain": "PROCESS",
                "finding": {
                    "finding_type": "PROCESS_INFORMATION_AVAILABLE",
                    "severity": "LOW",
                },
            },
        ]
    )

    assert result["patterns"] == []


def test_memory_and_process_findings_form_system_pattern():
    result = SystemWideProblemCorrelation().analyze(
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

    assert len(result["patterns"]) == 1


def test_memory_process_pattern_has_expected_type():
    result = SystemWideProblemCorrelation().analyze(
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

    assert (
        result["patterns"][0]["type"]
        == "SYSTEM_RESOURCE_PRESSURE"
    )


def test_pattern_preserves_domains():
    result = SystemWideProblemCorrelation().analyze(
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

    assert result["patterns"][0]["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_pattern_preserves_findings():
    result = SystemWideProblemCorrelation().analyze(
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

    assert len(
        result["patterns"][0]["findings"]
    ) == 2


def test_pattern_preserves_evidence():
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

    result = SystemWideProblemCorrelation().analyze(
        evidence
    )

    assert (
        result["patterns"][0]["evidence"]
        == evidence
    )


def test_resource_pattern_has_medium_confidence():
    result = SystemWideProblemCorrelation().analyze(
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

    assert (
        result["patterns"][0]["confidence"]
        == "MEDIUM"
    )


def test_high_process_commit_usage_also_forms_pattern():
    result = SystemWideProblemCorrelation().analyze(
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
                    "finding_type": "HIGH_COMMIT_USAGE",
                    "severity": "WARNING",
                },
            },
        ]
    )

    assert len(result["patterns"]) == 1


def test_service_and_network_findings_form_pattern():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": "SERVICE",
                "finding": {
                    "finding_type": "SERVICE_FAILURE",
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
    )

    assert len(result["patterns"]) == 1


def test_service_network_pattern_has_expected_type():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": "SERVICE",
                "finding": {
                    "finding_type": "SERVICE_FAILURE",
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
    )

    assert (
        result["patterns"][0]["type"]
        == "SERVICE_NETWORK_DEGRADATION"
    )


def test_service_network_pattern_preserves_domains():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": "SERVICE",
                "finding": {
                    "finding_type": "SERVICE_FAILURE",
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
    )

    assert result["patterns"][0]["domains"] == [
        "NETWORK",
        "SERVICE",
    ]


def test_multiple_patterns_are_preserved():
    result = SystemWideProblemCorrelation().analyze(
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
            {
                "domain": "SERVICE",
                "finding": {
                    "finding_type": "SERVICE_FAILURE",
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
    )

    assert len(result["patterns"]) == 2


def test_pattern_count_matches_patterns():
    result = SystemWideProblemCorrelation().analyze(
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
        }
        ]
    )

    assert (
        result["pattern_count"]
        == len(result["patterns"])
    )


def test_domain_names_are_normalized():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": " memory ",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            },
            {
                "domain": "Process",
                "finding": {
                    "finding_type": "HIGH_PROCESS_MEMORY",
                    "severity": "WARNING",
                },
            },
        ]
    )

    assert result["patterns"][0]["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_malformed_evidence_is_ignored():
    result = SystemWideProblemCorrelation().analyze(
        [
            None,
            "invalid",
            {},
            {
                "domain": "MEMORY",
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

    assert result["patterns"] == []


def test_missing_domain_is_ignored():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
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

    assert result["patterns"] == []


def test_missing_finding_is_ignored():
    result = SystemWideProblemCorrelation().analyze(
        [
            {
                "domain": "MEMORY",
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

    assert result["patterns"] == []


def test_input_is_not_mutated():
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

    original = [
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

    SystemWideProblemCorrelation().analyze(
        evidence
    )

    assert evidence == original


def test_result_has_stable_contract():
    result = SystemWideProblemCorrelation().analyze([])

    assert set(result.keys()) == {
        "patterns",
        "pattern_count",
    }


def test_correlation_does_not_claim_root_cause():
    result = SystemWideProblemCorrelation().analyze(
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

    assert "root_cause" not in result
    assert "primary_root_cause" not in result


def test_correlation_does_not_generate_remediation():
    result = SystemWideProblemCorrelation().analyze(
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

    assert "remediation" not in result


def test_duplicate_evidence_does_not_create_duplicate_pattern():
    result = SystemWideProblemCorrelation().analyze(
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
            {
                "domain": "MEMORY",
                "finding": {
                    "finding_type": "MEMORY_PRESSURE",
                    "severity": "WARNING",
                },
            },
        ]
    )

    assert len(result["patterns"]) == 1

