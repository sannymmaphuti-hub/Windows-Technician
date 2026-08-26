from engine.collectors.network_collector import NetworkCollector


def test_network_collector_returns_dictionary():

    collector = NetworkCollector()

    result = collector.collect()

    assert isinstance(result, dict)


def test_network_collector_contains_adapters():

    collector = NetworkCollector()

    result = collector.collect()

    assert "adapters" in result


def test_network_collector_adapters_are_list():

    collector = NetworkCollector()

    result = collector.collect()

    assert isinstance(result["adapters"], list)


def test_network_adapter_structure():

    collector = NetworkCollector()

    result = collector.collect()

    for adapter in result["adapters"]:

        assert "name" in adapter
        assert "ip_address" in adapter
        assert "netmask" in adapter