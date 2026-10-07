# ==========================================
# Windows Technician v0.9
# CROSS-DOMAIN SYSTEM EVIDENCE
# ==========================================

import pytest

from engine.cross_domain_system_evidence import (
    CrossDomainSystemEvidence,
)


def test_empty_domains_produce_empty_evidence():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect()

    assert result["evidence"] == []
    assert result["evidence_count"] == 0
    assert result["domains"] == []


def test_single_domain_finding_becomes_system_evidence():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            }
        }
    )

    assert result["evidence_count"] == 1
    assert result["domains"] == ["MEMORY"]

    item = result["evidence"][0]

    assert item["domain"] == "MEMORY"
    assert item["finding"] == "MEMORY_PRESSURE"


def test_multiple_domains_are_combined():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            },
            "PROCESS": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ]
            },
        }
    )

    assert result["evidence_count"] == 2

    assert result["evidence"] == [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "PROCESS",
            "finding": "HIGH_PROCESS_MEMORY",
        },
    ]


def test_multiple_findings_from_one_domain_are_preserved():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE",
                    "HIGH_COMMIT_USAGE",
                    "LOW_AVAILABLE_MEMORY",
                ]
            }
        }
    )

    assert result["evidence_count"] == 3

    assert result["evidence"] == [
        {
            "domain": "MEMORY",
            "finding": "MEMORY_PRESSURE",
        },
        {
            "domain": "MEMORY",
            "finding": "HIGH_COMMIT_USAGE",
        },
        {
            "domain": "MEMORY",
            "finding": "LOW_AVAILABLE_MEMORY",
        },
    ]


def test_domain_context_is_preserved():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ],
                "signals": [
                    "MEMORY_SIGNAL"
                ],
            },
            "PROCESS": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ],
                "signals": [
                    "PROCESS_SIGNAL"
                ],
            },
        }
    )

    assert result["domain_context"]["MEMORY"] == {
        "findings": [
            "MEMORY_PRESSURE"
        ],
        "signals": [
            "MEMORY_SIGNAL"
        ],
    }

    assert result["domain_context"]["PROCESS"] == {
        "findings": [
            "HIGH_PROCESS_MEMORY"
        ],
        "signals": [
            "PROCESS_SIGNAL"
        ],
    }


def test_domain_names_are_normalized():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "memory": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            },
            " process ": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ]
            },
        }
    )

    assert result["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_empty_domain_names_are_ignored():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "": {
                "findings": [
                    "INVALID"
                ]
            },
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            },
        }
    )

    assert result["evidence_count"] == 1
    assert result["domains"] == ["MEMORY"]


def test_invalid_domain_payloads_are_ignored():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": None,
            "PROCESS": "invalid",
            "DISK": {
                "findings": [
                    "LOW_FREE_SPACE"
                ]
            },
        }
    )

    assert result["evidence_count"] == 1
    assert result["domains"] == ["DISK"]


def test_missing_findings_do_not_create_fake_evidence():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "signals": [
                    "MEMORY_SIGNAL"
                ]
            }
        }
    )

    assert result["evidence"] == []
    assert result["evidence_count"] == 0


def test_non_list_findings_are_ignored():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": "MEMORY_PRESSURE"
            }
        }
    )

    assert result["evidence"] == []
    assert result["evidence_count"] == 0


def test_duplicate_findings_are_preserved():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE",
                    "MEMORY_PRESSURE",
                ]
            }
        }
    )

    assert result["evidence_count"] == 2


def test_evidence_retains_provenance():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "NETWORK": {
                "findings": [
                    "NETWORK_DEGRADED"
                ]
            }
        }
    )

    item = result["evidence"][0]

    assert item["domain"] == "NETWORK"
    assert item["finding"] == "NETWORK_DEGRADED"


def test_collection_does_not_create_relationships():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            },
            "PROCESS": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ]
            },
        }
    )

    assert result["relationships"] == []


def test_collection_does_not_create_root_causes():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            },
            "PROCESS": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ]
            },
        }
    )

    assert result["root_causes"] == []
    assert result["primary_root_cause"] is None


def test_input_is_not_mutated():
    evidence = CrossDomainSystemEvidence()

    domains = {
        "MEMORY": {
            "findings": [
                "MEMORY_PRESSURE"
            ]
        }
    }

    original = {
        "MEMORY": {
            "findings": [
                "MEMORY_PRESSURE"
            ]
        }
    }

    evidence.collect(
        domains=domains
    )

    assert domains == original


def test_non_mapping_domains_are_rejected():
    evidence = CrossDomainSystemEvidence()

    with pytest.raises(ValueError):
        evidence.collect(
            domains=[
                "MEMORY"
            ]
        )


def test_result_has_stable_contract():
    evidence = CrossDomainSystemEvidence()

    result = evidence.collect(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            }
        }
    )

    expected_keys = {
        "evidence",
        "evidence_count",
        "domains",
        "domain_context",
        "relationships",
        "root_causes",
        "primary_root_cause",
    }

    assert set(result.keys()) == expected_keys

