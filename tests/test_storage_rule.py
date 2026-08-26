from engine.rules.storage_rule import StorageFreeSpaceRule


def test_storage_rule_name():

    rule = StorageFreeSpaceRule()

    assert rule.name == "Storage Free Space Rule"


def test_storage_rule_category():

    rule = StorageFreeSpaceRule()

    assert rule.category == "STORAGE"


def test_storage_normal_free_space():

    rule = StorageFreeSpaceRule()

    result = rule.evaluate({
        "free_percent": 35
    })

    assert result is None


def test_storage_warning_free_space():

    rule = StorageFreeSpaceRule()

    result = rule.evaluate({
        "free_percent": 15
    })

    assert result["category"] == "STORAGE"
    assert result["severity"] == "WARNING"
    assert result["confidence"] == 0.85


def test_storage_critical_free_space():

    rule = StorageFreeSpaceRule()

    result = rule.evaluate({
        "free_percent": 5
    })

    assert result["category"] == "STORAGE"
    assert result["severity"] == "CRITICAL"
    assert result["confidence"] == 0.95


def test_storage_missing_free_space():

    rule = StorageFreeSpaceRule()

    result = rule.evaluate({})

    assert result is None