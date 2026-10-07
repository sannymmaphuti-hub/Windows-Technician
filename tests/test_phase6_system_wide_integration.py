# ==========================================
# Windows Technician v0.9
# PHASE 6 SYSTEM-WIDE INTEGRATION & LOCK
# ==========================================

from copy import deepcopy

import pytest

from engine.cross_domain_system_evidence import (
    CrossDomainSystemEvidence,
)
from engine.system_level_investigation import (
    SystemLevelInvestigation,
)
from engine.system_level_recommendations import (
    SystemLevelRecommendations,
)
from engine.system_health_model import (
    SystemHealthModel,
)
from engine.system_problem_relationships import (
    SystemProblemRelationships,
)
from engine.system_root_cause_reasoning import (
    SystemRootCauseReasoning,
)
from engine.system_wide_intelligence import (
    SystemWideIntelligence,
)
from engine.system_wide_problem_correlation import (
    SystemWideProblemCorrelation,
)


@pytest.fixture
def domains():
    return {
        "MEMORY": {
            "findings": [
                {
                    "finding_type": "MEMORY_PRESSURE",
                    "category": "MEMORY",
                    "severity": "WARNING",
                    "description": (
                        "System memory pressure "
                        "was detected."
                    ),
                }
            ],
        },
        "PROCESS": {
            "findings": [
                {
                    "finding_type": "HIGH_PROCESS_MEMORY",
                    "category": "PROCESS",
                    "severity": "HIGH",
                    "description": (
                        "A process is consuming "
                        "significant memory."
                    ),
                }
            ],
        },
        "SERVICE": {
            "findings": [
                {
                    "finding_type": "SERVICE_FAILURE",
                    "category": "SERVICE",
                    "severity": "WARNING",
                    "description": (
                        "A Windows service failure "
                        "was detected."
                    ),
                }
            ],
        },
        "NETWORK": {
            "findings": [
                {
                    "finding_type": (
                        "NETWORK_CONNECTIVITY_DEGRADED"
                    ),
                    "category": "NETWORK",
                    "severity": "MEDIUM",
                    "description": (
                        "Network connectivity "
                        "appears degraded."
                    ),
                }
            ],
        },
    }


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


def test_phase6_pipeline_constructs_system_intelligence(
    intelligence,
    domains,
):
    result = intelligence.analyze(domains)

    assert result["status"] == "ACTIVE"
    assert result["domain_count"] == 4
    assert result["domains"] == [
        "MEMORY",
        "NETWORK",
        "PROCESS",
        "SERVICE",
    ]


def test_phase6_pipeline_collects_cross_domain_evidence(
    intelligence,
    evidence_builder,
    domains,
):
    system = intelligence.analyze(domains)

    result = evidence_builder.collect(
        system["domain_data"]
    )

    assert result["evidence_count"] == 4

    assert {
        item["domain"]
        for item in result["evidence"]
    } == {
        "MEMORY",
        "PROCESS",
        "SERVICE",
        "NETWORK",
    }


def test_phase6_pipeline_preserves_structured_findings(
    evidence_builder,
    domains,
):
    result = evidence_builder.collect(domains)

    findings = [
        item["finding"]
        for item in result["evidence"]
    ]

    assert all(
        isinstance(finding, dict)
        for finding in findings
    )

    assert {
        finding["finding_type"]
        for finding in findings
    } == {
        "MEMORY_PRESSURE",
        "HIGH_PROCESS_MEMORY",
        "SERVICE_FAILURE",
        "NETWORK_CONNECTIVITY_DEGRADED",
    }


def test_phase6_pipeline_detects_relationships(
    evidence_builder,
    relationships,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    result = relationships.analyze(
        evidence["evidence"]
    )

    assert result["relationship_count"] == 1

    relationship = result["relationships"][0]

    assert relationship["type"] == (
        "RESOURCE_INTERACTION"
    )
    assert relationship["confidence"] == "MEDIUM"
    assert relationship["domains"] == [
        "MEMORY",
        "PROCESS",
    ]


def test_phase6_relationship_does_not_claim_causality(
    evidence_builder,
    relationships,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    result = relationships.analyze(
        evidence["evidence"]
    )

    relationship = result["relationships"][0]

    assert "cause" not in relationship
    assert "root_cause" not in relationship
    assert relationship["confidence"] == "MEDIUM"


def test_phase6_pipeline_constructs_root_cause_candidates(
    evidence_builder,
    relationships,
    root_cause,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    relationship_result = relationships.analyze(
        evidence["evidence"]
    )

    result = root_cause.analyze(
        relationship_result["relationships"]
    )

    assert len(result["root_causes"]) == 1

    candidate = result["root_causes"][0]

    assert candidate["cause_type"] == (
        "PROCESS_RESOURCE_CONSUMPTION"
    )
    assert candidate["confidence"] == "MEDIUM"
    assert candidate["supporting_relationships"]


def test_phase6_root_cause_remains_a_candidate(
    evidence_builder,
    relationships,
    root_cause,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    relationship_result = relationships.analyze(
        evidence["evidence"]
    )

    result = root_cause.analyze(
        relationship_result["relationships"]
    )

    candidate = result["primary_root_cause"]

    assert candidate is not None
    assert "candidate" in candidate["explanation"].lower()
    assert "certainty" not in candidate
    assert "remediation" not in candidate


def test_phase6_health_model_evaluates_all_domains(
    health,
    domains,
):
    result = health.evaluate(domains)

    assert result["status"] == "WARNING"
    assert result["coverage"] == "SYSTEM_WIDE"

    assert result["domains"] == [
        "MEMORY",
        "NETWORK",
        "PROCESS",
        "SERVICE",
    ]

    assert result["health_score"] == 10


def test_phase6_health_model_preserves_domain_health(
    health,
    domains,
):
    result = health.evaluate(domains)

    assert result["domain_health"] == {
        "MEMORY": "WARNING",
        "NETWORK": "DEGRADED",
        "PROCESS": "WARNING",
        "SERVICE": "WARNING",
    }


def test_phase6_pipeline_detects_system_patterns(
    evidence_builder,
    correlation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    result = correlation.analyze(
        evidence["evidence"]
    )

    assert result["pattern_count"] == 2

    pattern_types = {
        pattern["type"]
        for pattern in result["patterns"]
    }

    assert pattern_types == {
        "SYSTEM_RESOURCE_PRESSURE",
        "SERVICE_NETWORK_DEGRADATION",
    }


def test_phase6_correlation_preserves_evidence(
    evidence_builder,
    correlation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    result = correlation.analyze(
        evidence["evidence"]
    )

    for pattern in result["patterns"]:
        assert pattern["evidence"]
        assert pattern["findings"]
        assert pattern["domains"]


def test_phase6_correlation_does_not_create_root_causes(
    evidence_builder,
    correlation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    result = correlation.analyze(
        evidence["evidence"]
    )

    for pattern in result["patterns"]:
        assert "root_cause" not in pattern
        assert "primary_root_cause" not in pattern
        assert "cause" not in pattern


def test_phase6_investigation_prioritizes_system_patterns(
    evidence_builder,
    correlation,
    investigation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    patterns = correlation.analyze(
        evidence["evidence"]
    )["patterns"]

    findings = evidence["evidence"]

    result = investigation.investigate(
        {
            "findings": findings,
            "patterns": patterns,
        }
    )

    assert result["target_count"] == 6

    assert all(
        target["type"] == "SYSTEM_PATTERN"
        for target in result["targets"][:2]
    )


def test_phase6_investigation_produces_questions(
    evidence_builder,
    correlation,
    investigation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    patterns = correlation.analyze(
        evidence["evidence"]
    )["patterns"]

    result = investigation.investigate(
        {
            "findings": evidence["evidence"],
            "patterns": patterns,
        }
    )

    assert result["targets"]

    for target in result["targets"]:
        assert target["question"]
        assert isinstance(
            target["question"],
            str,
        )


def test_phase6_investigation_does_not_execute_actions(
    evidence_builder,
    correlation,
    investigation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    patterns = correlation.analyze(
        evidence["evidence"]
    )["patterns"]

    result = investigation.investigate(
        {
            "findings": evidence["evidence"],
            "patterns": patterns,
        }
    )

    for target in result["targets"]:
        assert "execute" not in target
        assert "executed" not in target
        assert "remediation" not in target


def test_phase6_recommendations_are_not_remediation(
    evidence_builder,
    correlation,
    recommendations,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    patterns = correlation.analyze(
        evidence["evidence"]
    )["patterns"]

    result = recommendations.generate(
        {
            "findings": evidence["evidence"],
            "patterns": patterns,
        }
    )

    assert result["recommendation_count"] == 6

    for recommendation in result["recommendations"]:
        assert recommendation["action"]
        assert recommendation["rationale"]
        assert "execute" not in recommendation
        assert "executed" not in recommendation
        assert "remediation" not in recommendation


def test_phase6_full_pipeline_has_no_remediation_surface(
    intelligence,
    evidence_builder,
    relationships,
    root_cause,
    health,
    correlation,
    investigation,
    recommendations,
    domains,
):
    system = intelligence.analyze(domains)

    evidence = evidence_builder.collect(
        system["domain_data"]
    )

    relationship_result = relationships.analyze(
        evidence["evidence"]
    )

    root_result = root_cause.analyze(
        relationship_result["relationships"]
    )

    health_result = health.evaluate(
        system["domain_data"]
    )

    correlation_result = correlation.analyze(
        evidence["evidence"]
    )

    investigation_result = investigation.investigate(
        {
            "findings": evidence["evidence"],
            "patterns": correlation_result[
                "patterns"
            ],
        }
    )

    recommendation_result = recommendations.generate(
        {
            "findings": evidence["evidence"],
            "patterns": correlation_result[
                "patterns"
            ],
        }
    )

    pipeline = {
        "system": system,
        "evidence": evidence,
        "relationships": relationship_result,
        "root_causes": root_result,
        "health": health_result,
        "correlation": correlation_result,
        "investigation": investigation_result,
        "recommendations": recommendation_result,
    }

    assert pipeline["system"]["remediation"] is None
    assert pipeline["relationships"]["root_causes"] == []
    assert pipeline["relationships"][
        "primary_root_cause"
    ] is None

    assert pipeline["root_causes"]["root_causes"]
    assert pipeline["root_causes"][
        "primary_root_cause"
    ] is not None

    assert pipeline["evidence"]["root_causes"] == []
    assert pipeline["evidence"][
        "primary_root_cause"
    ] is None

    assert pipeline["recommendations"][
        "recommendations"
    ]

    assert not any(
        "execute" in item
        for item in pipeline[
            "recommendations"
        ]["recommendations"]
    )


def test_phase6_layers_do_not_mutate_source_domains(
    intelligence,
    evidence_builder,
    health,
    domains,
):
    original = deepcopy(domains)

    system = intelligence.analyze(domains)
    evidence_builder.collect(
        system["domain_data"]
    )
    health.evaluate(
        system["domain_data"]
    )

    assert domains == original


def test_phase6_layers_do_not_mutate_evidence(
    evidence_builder,
    relationships,
    correlation,
    domains,
):
    evidence = evidence_builder.collect(
        domains
    )

    original = deepcopy(
        evidence["evidence"]
    )

    relationships.analyze(
        evidence["evidence"]
    )

    correlation.analyze(
        evidence["evidence"]
    )

    assert evidence["evidence"] == original

def test_phase6_system_intelligence_handles_empty_input(
    intelligence,
):
    result = intelligence.analyze(None)

    assert result["status"] == "INCOMPLETE"
    assert result["domain_count"] == 0
    assert result["domains"] == []
    assert result["domain_data"] == {}


@pytest.mark.parametrize(
    "bad_input",
    [
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_phase6_system_intelligence_rejects_invalid_domain_mapping(
    intelligence,
    bad_input,
):
    with pytest.raises(ValueError):
        intelligence.analyze(bad_input)


@pytest.mark.parametrize(
    "bad_input",
    [
        None,
        {},
        "invalid",
        123,
    ],
)
def test_phase6_relationship_layer_rejects_invalid_input(
    relationships,
    bad_input,
):
    if bad_input == {}:
        with pytest.raises(ValueError):
            relationships.analyze(bad_input)
        return

    with pytest.raises(ValueError):
        relationships.analyze(bad_input)


def test_phase6_empty_pipeline_is_safe(
    intelligence,
    evidence_builder,
    relationships,
    root_cause,
    health,
    correlation,
    investigation,
    recommendations,
):
    system = intelligence.analyze({})

    evidence = evidence_builder.collect(
        system["domain_data"]
    )

    relationship_result = relationships.analyze(
        evidence["evidence"]
    )

    root_result = root_cause.analyze(
        relationship_result["relationships"]
    )

    health_result = health.evaluate(
        system["domain_data"]
    )

    correlation_result = correlation.analyze(
        evidence["evidence"]
    )

    investigation_result = investigation.investigate(
        {
            "findings": evidence["evidence"],
            "patterns": correlation_result[
                "patterns"
            ],
        }
    )

    recommendation_result = recommendations.generate(
        {
            "findings": evidence["evidence"],
            "patterns": correlation_result[
                "patterns"
            ],
        }
    )

    assert system["status"] == "INCOMPLETE"
    assert evidence["evidence_count"] == 0
    assert relationship_result[
        "relationship_count"
    ] == 0
    assert root_result["root_causes"] == []
    assert health_result["status"] == "INCOMPLETE"
    assert correlation_result["pattern_count"] == 0
    assert investigation_result["target_count"] == 0
    assert recommendation_result[
        "recommendation_count"
    ] == 0

