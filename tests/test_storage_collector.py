from engine.collectors.storage_collector import StorageCollector


def test_storage_collector_name():

    collector = StorageCollector()

    assert collector.name == "Storage Collector"


def test_storage_collector_category():

    collector = StorageCollector()

    assert collector.category == "STORAGE"


def test_storage_collector_returns_list():

    collector = StorageCollector()

    result = collector.collect()

    assert isinstance(result, list)


def test_storage_collector_returns_valid_devices():

    collector = StorageCollector()

    result = collector.collect()

    for device in result:

        assert isinstance(device, dict)

        required_fields = [
            "device",
            "mountpoint",
            "filesystem",
            "total_gb",
            "used_gb",
            "free_gb",
            "usage_percent"
        ]

        for field in required_fields:

            assert field in device


def test_storage_collector_values_are_valid():

    collector = StorageCollector()

    result = collector.collect()

    for device in result:

        assert device["total_gb"] >= 0

        assert device["used_gb"] >= 0

        assert device["free_gb"] >= 0

        assert 0 <= device["usage_percent"] <= 100