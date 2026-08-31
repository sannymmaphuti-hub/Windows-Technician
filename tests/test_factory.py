# ==========================================

# Windows Technician v0.3

# FACTORY TESTS

# ==========================================

from engine.factory import create_diagnostic_engine

def test_factory_returns_analyzer():

    analyzer = create_diagnostic_engine()

    assert analyzer is not None

    assert hasattr(analyzer, "collectors")
    assert hasattr(analyzer, "rules")
    assert hasattr(analyzer, "engine")

def test_factory_configures_all_collectors():

    analyzer = create_diagnostic_engine()

    categories = {
        collector.category
        for collector in analyzer.collectors
    }

    assert categories == {
        "CPU",
        "MEMORY",
        "STORAGE",
        "NETWORK",
        "GPU",
        "PROCESS"
    }

def test_factory_configures_all_rules():

    analyzer = create_diagnostic_engine()

    categories = {
        rule.category
        for rule in analyzer.rules
    }

    assert categories == {
        "CPU",
        "MEMORY",
        "STORAGE",
        "NETWORK",
        "GPU"
    }

def test_factory_configures_recommendation_engine():

    analyzer = create_diagnostic_engine()

    assert analyzer.engine.recommendation_engine is not None


def test_factory_engine_contains_all_rules():

    analyzer = create_diagnostic_engine()

    assert len(analyzer.engine.rules) == 5
