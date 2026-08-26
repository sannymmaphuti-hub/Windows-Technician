from engine.recommendation_engine import RecommendationEngine


def test_recommendation_engine_cpu_warning():

    engine = RecommendationEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization."
    }

    recommendation = engine.get_recommendation(finding)

    assert recommendation is not None
    assert "CPU" in recommendation


def test_recommendation_engine_cpu_critical():

    engine = RecommendationEngine()

    finding = {
        "category": "CPU",
        "severity": "CRITICAL",
        "message": "Critically high CPU utilization."
    }

    recommendation = engine.get_recommendation(finding)

    assert recommendation is not None
    assert "CPU" in recommendation


def test_recommendation_engine_memory_warning():

    engine = RecommendationEngine()

    finding = {
        "category": "MEMORY",
        "severity": "WARNING",
        "message": "High memory usage."
    }

    recommendation = engine.get_recommendation(finding)

    assert recommendation is not None
    assert "memory" in recommendation.lower()


def test_recommendation_engine_storage_critical():

    engine = RecommendationEngine()

    finding = {
        "category": "STORAGE",
        "severity": "CRITICAL",
        "message": "Critically low storage."
    }

    recommendation = engine.get_recommendation(finding)

    assert recommendation is not None
    assert "disk" in recommendation.lower()


def test_recommendation_engine_unknown_finding():

    engine = RecommendationEngine()

    finding = {
        "category": "UNKNOWN",
        "severity": "WARNING",
        "message": "Unknown problem."
    }

    recommendation = engine.get_recommendation(finding)

    assert recommendation is None


def test_recommendation_engine_multiple_findings():

    engine = RecommendationEngine()

    findings = [
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "High CPU."
        },

        {
            "category": "MEMORY",
            "severity": "CRITICAL",
            "message": "High memory."
        },

        {
            "category": "STORAGE",
            "severity": "WARNING",
            "message": "Low storage."
        }
    ]

    recommendations = engine.get_recommendations(
        findings
    )

    assert len(recommendations) == 3

    assert recommendations[0]["category"] == "CPU"
    assert recommendations[1]["category"] == "MEMORY"
    assert recommendations[2]["category"] == "STORAGE"