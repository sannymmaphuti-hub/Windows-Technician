from engine.finding import Finding
from engine.legacy_finding_adapter import LegacyFindingAdapter
from engine.recommendation_engine import RecommendationEngine
from engine.recommendation_rule import RecommendationRule


class _MatchingRule(RecommendationRule):

    def matches(self, finding):
        return isinstance(finding, Finding)

    def create_recommendation(self, finding):
        return finding


class _TrackingAdapter(LegacyFindingAdapter):

    def __init__(self):
        self.converted = []

    def convert(self, legacy_finding):
        self.converted.append(legacy_finding)
        return super().convert(legacy_finding)


def test_recommendation_engine_delegates_legacy_conversion_to_adapter():
    adapter = _TrackingAdapter()
    engine = RecommendationEngine(adapter=adapter)

    legacy_finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "High CPU usage detected.",
    }

    engine.register_rule(_MatchingRule())

    recommendations = engine.get_recommendations(
        [legacy_finding]
    )

    assert adapter.converted == [legacy_finding]
    assert len(recommendations) == 1
    assert isinstance(recommendations[0], Finding)
