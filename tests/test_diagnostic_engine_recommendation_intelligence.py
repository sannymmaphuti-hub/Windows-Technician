import pytest

from engine.diagnostic_engine import DiagnosticEngine
from engine.finding import Finding
from engine.memory_recommendation_rule import (
    MemoryRecommendationRule,
)
from engine.recommendation import Recommendation
from engine.recommendation_engine import RecommendationEngine
from engine.root_cause_reasoning import RootCauseReasoning


class FakeRule:

    category = "MEMORY"

    def evaluate(self, evidence):
        return {
            "category": "MEMORY",
            "severity": "WARNING",
            "message": "High memory usage detected.",
        }


class FakeRecommendationEngine:

    def __init__(self):
        self.received_findings = None

    def get_recommendations(self, findings):
        self.received_findings = findings

        return [
            Recommendation(
                recommendation_type="REVIEW_MEMORY",
                category="MEMORY",
                priority="HIGH",
                description=(
                    "Review memory-intensive processes."
                ),
                rationale=(
                    "High memory pressure was detected."
                ),
            )
        ]


def create_engine(recommendation_engine=None):
    engine = DiagnosticEngine(
        recommendation_engine=recommendation_engine,
        root_cause_reasoning=RootCauseReasoning(),
    )

    engine.add_rule(FakeRule())

    return engine


def test_diagnostic_engine_accepts_recommendation_engine():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    assert engine.recommendation_engine is (
        recommendation_engine
    )


def test_diagnostic_engine_passes_findings_to_recommendation_engine():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 95,
        }
    }

    engine.diagnose(evidence)

    assert recommendation_engine.received_findings is not None
    assert len(
        recommendation_engine.received_findings
    ) == 1


def test_diagnostic_engine_returns_recommendations():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 95,
        }
    }

    result = engine.diagnose(evidence)

    assert "recommendations" in result
    assert len(result["recommendations"]) == 1


def test_diagnostic_engine_preserves_recommendation_objects():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 95,
        }
    }

    result = engine.diagnose(evidence)

    recommendation = result["recommendations"][0]

    assert isinstance(
        recommendation,
        Recommendation,
    )


def test_diagnostic_engine_preserves_recommendation_type():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert (
        result["recommendations"][0].recommendation_type
        == "REVIEW_MEMORY"
    )


def test_diagnostic_engine_without_recommendation_engine_returns_empty_list():
    engine = create_engine(
        recommendation_engine=None
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert result["recommendations"] == []


def test_real_recommendation_engine_can_be_integrated():
    recommendation_engine = RecommendationEngine()

    recommendation_engine.register_rule(
        MemoryRecommendationRule()
    )

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert isinstance(
        recommendation,
        Recommendation,
    )

    assert (
        recommendation.recommendation_type
        == "REVIEW_MEMORY"
    )


def test_recommendation_intelligence_does_not_modify_findings():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    finding = result["findings"][0]

    assert finding["category"] == "MEMORY"
    assert finding["severity"] == "WARNING"
    assert finding["message"] == (
        "High memory usage detected."
    )


def test_recommendation_intelligence_does_not_create_remediation():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert "remediation" not in result
    assert "remediation_actions" not in result


def test_recommendation_intelligence_does_not_grant_authority():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    recommendation = result["recommendations"][0]

    assert recommendation.recommendation_type == (
        "REVIEW_MEMORY"
    )

    assert not hasattr(
        recommendation,
        "authorized",
    )


def test_diagnostic_engine_still_returns_root_cause_reasoning():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert "root_cause_reasoning" in result


def test_recommendations_are_generated_after_diagnosis():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 95,
            }
        }
    )

    assert result["total_findings"] == 1
    assert len(result["recommendations"]) == 1


def test_diagnose_can_be_run_again_with_recommendations():
    recommendation_engine = FakeRecommendationEngine()

    engine = create_engine(
        recommendation_engine=recommendation_engine
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 95,
        }
    }

    first_result = engine.diagnose(evidence)
    second_result = engine.diagnose(evidence)

    assert len(first_result["recommendations"]) == 1
    assert len(second_result["recommendations"]) == 1
    assert second_result["total_findings"] == 1