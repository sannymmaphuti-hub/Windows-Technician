from engine.collectors.cpu_collector import CPUCollector


def test_cpu_collector_returns_evidence():

    collector = CPUCollector()

    data = collector.collect()

    assert isinstance(data, dict)

    assert "physical_cores" in data
    assert "logical_processors" in data
    assert "usage_percent" in data
    assert "frequency_mhz" in data
    assert "status" in data
    assert "top_processes" in data


def test_cpu_collector_returns_valid_cpu_values():

    collector = CPUCollector()

    data = collector.collect()

    assert data["physical_cores"] >= 1
    assert data["logical_processors"] >= 1
    assert 0 <= data["usage_percent"] <= 100
    assert data["frequency_mhz"] >= 0


def test_cpu_collector_returns_process_list():

    collector = CPUCollector()

    data = collector.collect()

    assert isinstance(data["top_processes"], list)