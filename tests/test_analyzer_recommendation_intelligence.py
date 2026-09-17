from engine.analyzer import Analyzer
from engine.memory_recommendation_rule import MemoryRecommendationRule
from engine.recommendation_engine import RecommendationEngine
from engine.rules.memory_rule import MemoryUsageRule


class FakeMemoryCollector:

    category = "MEMORY"

    def collect(self):

        return {
            "usage_percent": 95.0
        }


def test_analyzer_generates_recommendations_from_final_findings():

    recommendation_engine = RecommendationEngine()

    recommendation_engine.register_rule(
        MemoryRecommendationRule()
    )

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector()
        ],
        rules=[
            MemoryUsageRule()
        ],
        recommendation_engine=recommendation_engine,
    )

    result = analyzer.analyze()

    recommendations = (
        result["diagnosis"]["recommendations"]
    )

    assert recommendations