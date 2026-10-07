# ==========================================
# Windows Technician v0.9
# SYSTEM-WIDE INTELLIGENCE ARCHITECTURE
# ==========================================

import pytest

from engine.system_wide_intelligence import (
    SystemWideIntelligence,
)


def test_empty_system_produces_incomplete_context():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze()

    assert result["status"] == "INCOMPLETE"
    assert result["domain_count"] == 0
    assert result["domains"] == []
    assert result["domain_data"] == {}
    assert result["domain_findings"] == {}


def test_single_domain_produces_partial_context():
    intelligence = SystemWideIntelligence()

    domains = {
        "MEMORY": {
            "findings": [
                "MEMORY_PRESSURE"
            ]
        }
    }

    result = intelligence.analyze(
        domains=domains
    )

    assert result["status"] == "PARTIAL"
    assert result["domain_count"] == 1
    assert result["domains"] == ["MEMORY"]


def test_multiple_domains_produce_active_context():
    intelligence = SystemWideIntelligence()

    domains = {
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

    result = intelligence.analyze(
        domains=domains
    )

    assert result["status"] == "ACTIVE"
    assert result["domain_count"] == 2
    assert result["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_domain_payloads_are_preserved():
    intelligence = SystemWideIntelligence()

    domains = {
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
        },
    }

    result = intelligence.analyze(
        domains=domains
    )

    assert result["domain_data"] == domains


def test_domain_findings_are_preserved_with_domain_context():
    intelligence = SystemWideIntelligence()

    domains = {
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

    result = intelligence.analyze(
        domains=domains
    )

    assert result["domain_findings"] == domains


def test_domain_names_are_normalized():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "memory": {
                "findings": []
            },
            " process ": {
                "findings": []
            },
        }
    )

    assert result["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_empty_domain_names_are_ignored():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "": {
                "findings": [
                    "INVALID"
                ]
            },
            "MEMORY": {
                "findings": []
            },
        }
    )

    assert result["domains"] == ["MEMORY"]
    assert result["domain_count"] == 1


def test_missing_domain_payload_is_ignored():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "MEMORY": None,
            "PROCESS": {
                "findings": [
                    "HIGH_PROCESS_MEMORY"
                ]
            },
        }
    )

    assert result["domains"] == ["PROCESS"]
    assert result["domain_count"] == 1


def test_invalid_domain_payload_is_ignored():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "MEMORY": "invalid",
            "PROCESS": {
                "findings": []
            },
        }
    )

    assert result["domains"] == ["PROCESS"]
    assert result["domain_count"] == 1


def test_relationship_surface_is_empty_until_relationship_phase():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
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


def test_root_cause_is_not_inferred_by_architecture_layer():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
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
    assert result["root_cause_confidence"] == "NONE"


def test_system_findings_are_not_invented():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
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

    assert result["system_findings"] == []


def test_recommendations_are_not_generated():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            }
        }
    )

    assert result["recommendations"] == []


def test_remediation_is_outside_system_intelligence():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "MEMORY": {
                "findings": [
                    "MEMORY_PRESSURE"
                ]
            }
        }
    )

    assert result["remediation"] is None


def test_non_mapping_domains_are_rejected():
    intelligence = SystemWideIntelligence()

    with pytest.raises(ValueError):
        intelligence.analyze(
            domains=[
                "MEMORY"
            ]
        )


def test_input_is_not_mutated():
    intelligence = SystemWideIntelligence()

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

    intelligence.analyze(
        domains=domains
    )

    assert domains == original


def test_result_contains_stable_system_intelligence_contract():
    intelligence = SystemWideIntelligence()

    result = intelligence.analyze(
        domains={
            "MEMORY": {
                "findings": []
            }
        }
    )

    expected_keys = {
        "status",
        "domain_count",
        "domains",
        "domain_data",
        "domain_findings",
        "relationships",
        "system_findings",
        "root_causes",
        "primary_root_cause",
        "root_cause_confidence",
        "recommendations",
        "remediation",
    }

    assert set(result.keys()) == expected_keys

