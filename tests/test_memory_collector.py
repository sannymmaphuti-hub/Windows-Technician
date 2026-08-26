from engine.collectors.memory_collector import MemoryCollector


def test_memory_collector_name():

    collector = MemoryCollector()

    assert collector.name == "Memory Collector"


def test_memory_collector_category():

    collector = MemoryCollector()

    assert collector.category == "MEMORY"


def test_memory_collector_returns_data():

    collector = MemoryCollector()

    result = collector.collect()

    assert isinstance(result, dict)


def test_memory_collector_contains_required_fields():

    collector = MemoryCollector()

    result = collector.collect()

    required_fields = [
        "total_gb",
        "used_gb",
        "available_gb",
        "usage_percent"
    ]

    for field in required_fields:

        assert field in result


def test_memory_collector_values_are_valid():

    collector = MemoryCollector()

    result = collector.collect()

    assert result["total_gb"] > 0

    assert result["used_gb"] >= 0

    assert result["available_gb"] >= 0

    assert 0 <= result["usage_percent"] <= 100