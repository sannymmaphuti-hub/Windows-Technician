from engine.rules.cpu_rule import CPUUsageRule


def test_cpu_rule_name():

    rule = CPUUsageRule()

    assert rule.name == "CPU Usage Rule"


def test_cpu_normal_usage():

    rule = CPUUsageRule()

    result = rule.evaluate({
        "usage_percent": 50
    })

    assert result is None


def test_cpu_warning_usage():

    rule = CPUUsageRule()

    result = rule.evaluate({
        "usage_percent": 85
    })

    assert result["category"] == "CPU"
    assert result["severity"] == "WARNING"
    assert result["confidence"] == 0.85


def test_cpu_critical_usage():

    rule = CPUUsageRule()

    result = rule.evaluate({
        "usage_percent": 97
    })

    assert result["category"] == "CPU"
    assert result["severity"] == "CRITICAL"
    assert result["confidence"] == 0.95


def test_cpu_missing_usage():

    rule = CPUUsageRule()

    result = rule.evaluate({})

    assert result is None

def test_cpu_rule_has_category():

    rule = CPUUsageRule()

    assert rule.category == "CPU"