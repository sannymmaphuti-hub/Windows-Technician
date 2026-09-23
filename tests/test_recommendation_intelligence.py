import pytest

from engine.recommendation_intelligence import RecommendationIntelligence
from engine.recommendation_intelligence import RecommendationIntelligence
from engine.finding import Finding

def test_high_memory_finding_produces_memory_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "MEMORY",
                "severity": "HIGH",
            }
        ]
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.recommendation_type == "memory_review"
    assert recommendation.category == "MEMORY"
    assert recommendation.priority == "HIGH"


def test_recommendation_contains_rationale():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "MEMORY",
                "severity": "HIGH",
            }
        ]
    )

    assert recommendations[0].rationale


def test_unsupported_finding_does_not_create_arbitrary_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "UNKNOWN",
                "severity": "HIGH",
            }
        ]
    )

    assert recommendations == []


def test_empty_findings_produce_no_recommendations():
    intelligence = RecommendationIntelligence()

    assert intelligence.generate(findings=[]) == []

def test_high_cpu_finding_produces_cpu_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "CPU",
                "severity": "HIGH",
            }
        ]
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.recommendation_type == "cpu_review"
    assert recommendation.category == "CPU"
    assert recommendation.priority == "HIGH"


def test_high_storage_finding_produces_storage_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "STORAGE",
                "severity": "HIGH",
            }
        ]
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.recommendation_type == "storage_review"
    assert recommendation.category == "STORAGE"
    assert recommendation.priority == "HIGH"


def test_high_network_finding_produces_network_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "NETWORK",
                "severity": "HIGH",
            }
        ]
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.recommendation_type == "network_review"
    assert recommendation.category == "NETWORK"
    assert recommendation.priority == "HIGH"

def test_multiple_findings_produce_multiple_recommendations():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "MEMORY",
                "severity": "HIGH",
            },
            {
                "category": "CPU",
                "severity": "HIGH",
            },
            {
                "category": "NETWORK",
                "severity": "HIGH",
            },
        ]
    )

    assert len(recommendations) == 3

    recommendation_types = {
        recommendation.recommendation_type
        for recommendation in recommendations
    }

    assert recommendation_types == {
        "memory_review",
        "cpu_review",
        "network_review",
    }

def test_duplicate_findings_produce_one_recommendation():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=[
            {
                "category": "MEMORY",
                "severity": "HIGH",
            },
            {
                "category": "MEMORY",
                "severity": "HIGH",
            },
        ]
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == "memory_review"

def test_high_memory_finding_object_produces_recommendation():
    intelligence = RecommendationIntelligence()

    finding = Finding(
        finding_type="memory_pressure",
        description="High memory pressure detected.",
        category="MEMORY",
        severity="HIGH",
        supporting_signals=[],
    )

    recommendations = intelligence.generate(
        findings=[finding]
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == "memory_review"

from engine.diagnostic_case import DiagnosticCase


def test_recommendation_intelligence_generates_recommendations_for_diagnostic_case():
    case = DiagnosticCase()

    case.findings.append(
        Finding(
            finding_type="memory_pressure",
            description="High memory pressure detected.",
            category="MEMORY",
            severity="HIGH",
            supporting_signals=[],
        )
    )

    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(
        findings=case.findings
    )

    case.recommendations.extend(recommendations)

    assert len(case.recommendations) == 1
    assert (
        case.recommendations[0].recommendation_type
        == "memory_review"
    )

def test_diagnostic_case_generates_and_stores_recommendations():
    case = DiagnosticCase()

    case.findings.append(
        Finding(
            finding_type="memory_pressure",
            description="High memory pressure detected.",
            category="MEMORY",
            severity="HIGH",
            supporting_signals=[],
        )
    )

    recommendations = case.generate_recommendations()

    assert len(recommendations) == 1
    assert recommendations is case.recommendations
    assert (
        case.recommendations[0].recommendation_type
        == "memory_review"
    )

def test_diagnostic_case_generates_only_supported_unique_recommendations():
    case = DiagnosticCase()

    case.findings.extend(
        [
            Finding(
                finding_type="memory_pressure",
                description="High memory pressure detected.",
                category="MEMORY",
                severity="HIGH",
                supporting_signals=[],
            ),
            Finding(
                finding_type="memory_pressure_duplicate",
                description="Another high memory pressure finding.",
                category="MEMORY",
                severity="HIGH",
                supporting_signals=[],
            ),
            Finding(
                finding_type="cpu_pressure",
                description="High CPU pressure detected.",
                category="CPU",
                severity="HIGH",
                supporting_signals=[],
            ),
            Finding(
                finding_type="low_storage",
                description="Low-severity storage finding.",
                category="STORAGE",
                severity="LOW",
                supporting_signals=[],
            ),
        ]
    )

    recommendations = case.generate_recommendations()

    recommendation_types = {
        recommendation.recommendation_type
        for recommendation in recommendations
    }

    assert recommendation_types == {
        "memory_review",
        "cpu_review",
    }
    assert len(recommendations) == 2