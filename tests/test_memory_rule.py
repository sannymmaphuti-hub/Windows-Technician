from engine.rules.memory_rule import MemoryUsageRule


def test_memory_rule_name():

    rule = MemoryUsageRule()

    assert rule.name == "Memory Usage Rule"


def test_memory_rule_category():

    rule = MemoryUsageRule()

    assert rule.category == "MEMORY"


def test_memory_normal_usage():

    rule = MemoryUsageRule()

    result = rule.evaluate({
        "usage_percent": 50
    })

    assert result is None


def test_memory_warning_usage():

    rule = MemoryUsageRule()

    result = rule.evaluate({
        "usage_percent": 85
    })

    assert result["category"] == "MEMORY"
    assert result["severity"] == "WARNING"
    assert result["confidence"] == 0.85


def test_memory_critical_usage():

    rule = MemoryUsageRule()

    result = rule.evaluate({
        "usage_percent": 97
    })

    assert result["category"] == "MEMORY"
    assert result["severity"] == "CRITICAL"
    assert result["confidence"] == 0.95


def test_memory_missing_usage():

    rule = MemoryUsageRule()

    result = rule.evaluate({})

    assert result is None